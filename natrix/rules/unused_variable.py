from __future__ import annotations

from natrix.ast_node import FunctionDefNode
from natrix.rules.common import BaseRule, RuleRegistry


@RuleRegistry.register
class UnusedVariableRule(BaseRule):
    """
    Unused Variable Check

    Detects variables that are declared (via assignments like Assign, AnnAssign, and AugAssign)
    but never actually referenced (via Name nodes) within a function. It matches each declared
    variable to its assignment node and checks if it appears in any Name node usages.

    Example:
        def example_function():
            unused_var: uint256 = 42  # This line will be reported.
    """

    CODE = "NTX8"
    MESSAGE = "Variable '{}' is declared but never used."

    def __init__(self) -> None:
        super().__init__(
            severity="warning",
            code=self.CODE,
            message=self.MESSAGE,
        )

    def visit_FunctionDef(self, node: FunctionDefNode) -> None:
        # Gather all assignment-related nodes
        all_assigns = node.get_descendants(
            node_type=("AnnAssign", "Assign", "AugAssign")
        )

        # Collect the assigned variable names, excluding None, and map them to their declaration nodes
        # For each variable, we want to keep track of its first declaration (AnnAssign) if available
        assigned_var_nodes = {}
        for assign in all_assigns:
            var_name = assign.get("target.id")
            if var_name is not None:
                # If this is an AnnAssign (declaration) or we haven't seen this variable before, store it
                if assign.ast_type == "AnnAssign" or var_name not in assigned_var_nodes:
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

        # Collect all for loop target variables and map them to their correct nodes
        for_loop_targets = {}
        for_loops = node.get_descendants(node_type="For")
        for for_loop in for_loops:
            target_name = for_loop.get("target.target.id")
            if target_name is not None:
                # Find the Name node with the correct id and position
                target_nodes = for_loop.get_descendants(
                    node_type="Name", filters={"id": target_name}
                )
                if target_nodes:
                    # Use the first matching Name node
                    for_loop_targets[target_name] = target_nodes[0]

        # Check if this is a constructor function using the built-in property
        is_constructor = node.is_constructor

        # Get immutable variables if this is a constructor
        immutable_vars = node.immutable_vars if is_constructor else set()

        # Any remaining variable in assigned_var_nodes is unused
        for var_name, assign_node in assigned_var_nodes.items():
            # Skip reporting if the variable is named '_' and is a for loop target
            if var_name == "_" and var_name in for_loop_targets:
                continue

            # Skip immutable variables in constructor
            if is_constructor and var_name in immutable_vars:
                continue

            if var_name not in used_var_names:
                # If this is a for loop variable, use the correct node for the position
                if var_name in for_loop_targets:
                    self.add_issue(for_loop_targets[var_name], var_name)
                else:
                    self.add_issue(assign_node, var_name)
