from natrix.rules.common import BaseRule
from dpath import get


class UnusedVariableRule(BaseRule):
    def __init__(self):
        super().__init__(
            severity="warning",
            code="NTX008",
            message="Variable '{}' is declared but never used.",
        )
        self.declared_vars = {}  # Track variables declared in the current function
        self.in_declaration = False  # Track if currently in a declaration

    def visit_FunctionDef(self, node):
        # Initialize declared_vars for the current function
        self.declared_vars = {}

        # First, collect all variable declarations without marking anything as used
        self._collect_declarations(get(node, "body", default=[]))

        # Then, traverse the function body again to detect usage
        for child in node["body"]:
            self._detect_usage(child)

        # Report any variables that were declared but never used
        for var_name, var_info in self.declared_vars.items():
            if not var_info["is_used"]:
                # Directly pass the variable name as an argument for `add_issue`
                self.add_issue(
                    var_info["node"], var_name
                )  # Pass `var_name` as message argument

    def _collect_declarations(self, statements):
        """Collect all declared variables in the function body without marking them as used."""
        for stmt in statements:
            if stmt.get("ast_type") in ["Assign", "AnnAssign"]:
                target = get(stmt, "target", default={})
                if target.get("ast_type") == "Name":
                    var_name = target["id"]
                    # Store both the unused status and the declaration node
                    self.declared_vars[var_name] = {"is_used": False, "node": target}
            elif stmt.get("ast_type") in ["If", "For", "While"]:
                # Recursively collect declarations in nested blocks
                self._collect_declarations(get(stmt, "body", default=[]))
                self._collect_declarations(get(stmt, "orelse", default=[]))

    def _detect_usage(self, node):
        """Traverse the AST to mark declared variables as used."""
        if not isinstance(node, dict):
            return

        ast_type = node.get("ast_type", None)
        if ast_type == "Name" and not self.in_declaration:
            # If the name corresponds to a declared variable, mark it as used
            var_name = node.get("id", None)
            if var_name in self.declared_vars:
                self.declared_vars[var_name]["is_used"] = True

        elif ast_type in ["Assign", "AnnAssign"]:
            # Set in_declaration to True when visiting an assignment, to avoid self-referencing
            self.in_declaration = True
            self.generic_visit(node)  # Visit the assignment
            self.in_declaration = False

        else:
            # Recursively check for usage in all child nodes
            for key, value in node.items():
                if isinstance(value, dict):
                    self._detect_usage(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            self._detect_usage(item)
