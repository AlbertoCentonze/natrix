from natrix.ast_node import Node
from natrix.rules.common import BaseRule


class UnusedVariableRule(BaseRule):
    """
    Detects variables that are declared (via assignments like Assign, AnnAssign, and AugAssign)
    but never actually referenced (via Name nodes) within a function. It matches each declared
    variable to its assignment node and checks if it appears in any Name node usages.

    Example:
        def example_function():
            unused_var: uint256 = 42  # This line will be reported.
    """

    def __init__(self):
        super().__init__(
            severity="warning",
            code="NTX008",
            message="Variable '{}' is declared but never used.",
        )

    def visit_FunctionDef(self, node: Node):
        # Gather all assignment-related nodes
        all_assigns = node.get_descendants(
            node_type=("AnnAssign", "Assign", "AugAssign")
        )

        # Collect the assigned variable names, excluding None, and map them to their assignment nodes
        assigned_var_nodes = {}
        for assign in all_assigns:
            var_name = assign.get("target.id")
            if var_name is not None:
                assigned_var_nodes[var_name] = assign

        # Gather the node IDs for these assignments
        assigned_var_node_ids = [assign.get("target.node_id") for assign in all_assigns]

        # Collect all 'Name' nodes in the function
        all_names = node.get_descendants(node_type="Name")

        # Filter only those names that appear in our assigned variable set
        candidate_assigned_names = [
            name for name in all_names if name.get("id") in assigned_var_nodes
        ]

        # Determine which assigned variables are actually used
        used_var_names = set()
        for name in candidate_assigned_names:
            if name.get("node_id") not in assigned_var_node_ids:
                used_var_names.add(name.get("id"))

        # Any remaining variable in assigned_var_nodes is unused
        for var_name, assign_node in assigned_var_nodes.items():
            if var_name not in used_var_names:
                self.add_issue(assign_node, var_name)
