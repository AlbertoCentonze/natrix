from natrix.ast_node import Node, FunctionDefNode
from natrix.rules.common import BaseRule, RuleRegistry
import re


@RuleRegistry.register
class ArgNamingConventionRule(BaseRule):
    """
    Argument Naming Convention Check

    Ensures that function arguments follow a specified naming convention using a regex pattern.

    Example:
        def example_function(prefix_arg: uint256): # This line is correct if 'prefix_' is the required prefix.
    """

    CODE = "NTX11"
    MESSAGE = (
        "Function '{}' argument '{}' does not match the naming convention pattern '{}'."
    )

    def __init__(self, pattern=r"^_"):
        super().__init__(
            severity="warning",
            code=self.CODE,
            message=self.MESSAGE,
        )
        self.pattern = re.compile(pattern)

    def visit_FunctionDef(self, node: FunctionDefNode):
        # Collect declared arguments in a dictionary, {arg_name: arg_node}
        for arg_info in node.get("args.args"):
            arg_node = Node(arg_info)
            arg_name = arg_node.get("arg")
            if arg_name is not None:
                if not self.pattern.match(arg_name):
                    self.add_issue(
                        arg_node, node.get("name"), arg_name, self.pattern.pattern
                    )
