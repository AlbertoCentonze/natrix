from natrix.rules.common import BaseRule
from dpath import get


class CacheStorageVariableRule(BaseRule):
    def __init__(self):
        super().__init__(
            severity="optimization",
            code="NTX007",
            message="Variable '{}' is accessed multiple times; consider caching it to save gas.",
        )

    def visit_FunctionDef(self, node):
        # Dictionary to keep track of storage variable accesses
        # Key: variable name, Value: {'read_count': int}
        storage_vars = {}

        # Start traversing the function body
        self._traverse_statements(get(node, "body", default=[]), storage_vars)

    def _traverse_statements(self, statements, storage_vars):
        for stmt in statements:
            # Handle different statement types recursively
            if stmt["ast_type"] in ["Assign", "AnnAssign"]:
                self._handle_assignment(stmt, storage_vars)
            elif stmt["ast_type"] == "If":
                self._handle_if(stmt, storage_vars)
            elif stmt["ast_type"] == "Expr":
                self._handle_expr(stmt, storage_vars)
            elif stmt["ast_type"] == "Return":
                self._handle_return(stmt, storage_vars)
            # Add other statement types if necessary
            elif stmt["ast_type"] == "For":
                self._handle_for(stmt, storage_vars)
            elif stmt["ast_type"] == "While":
                self._handle_while(stmt, storage_vars)
            # ... and so on

    def _handle_assignment(self, stmt, storage_vars):
        target = get(stmt, "target", default={})
        value = get(stmt, "value", default={})

        # Check if the target is a storage variable (self.<variable>)
        if self._is_storage_variable(target):
            var_name = target["attr"]
            # Reset read count upon write
            storage_vars[var_name] = {"read_count": 0}
            # Also check if the value reads storage variables
            self._check_storage_reads(value, storage_vars)
        else:
            # Check if the value reads storage variables
            self._check_storage_reads(value, storage_vars)

    def _handle_if(self, stmt, storage_vars):
        # Check the condition
        test = get(stmt, "test", default={})
        self._check_storage_reads(test, storage_vars)

        # Copy the storage_vars to maintain separate counts in different branches
        self._traverse_statements(get(stmt, "body", default=[]), storage_vars.copy())
        self._traverse_statements(get(stmt, "orelse", default=[]), storage_vars.copy())

    def _handle_expr(self, stmt, storage_vars):
        value = get(stmt, "value", default={})
        self._check_storage_reads(value, storage_vars)

    def _handle_return(self, stmt, storage_vars):
        value = get(stmt, "value", default={})
        self._check_storage_reads(value, storage_vars)

    def _check_storage_reads(self, node, storage_vars):
        """Recursively check for storage variable reads in the given node."""
        if not isinstance(node, dict):
            return

        ast_type = get(node, "ast_type", default=None)
        if ast_type == "Attribute" and self._is_storage_variable(node):
            var_name = node["attr"]
            var_info = storage_vars.get(var_name, {"read_count": 0})

            var_info["read_count"] += 1

            storage_vars[var_name] = var_info

            # If read count reaches 2, suggest caching
            if var_info["read_count"] == 2:
                self.add_issue(node, var_name)
        else:
            # Recurse into child nodes
            for key, value in node.items():
                if isinstance(value, dict):
                    self._check_storage_reads(value, storage_vars)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            self._check_storage_reads(item, storage_vars)

    def _is_storage_variable(self, node):
        """Check if the node represents a storage variable access (self.<variable>)."""
        if get(node, "ast_type", default=None) == "Attribute":
            value = get(node, "value", default={})
            if (
                get(value, "ast_type", default=None) == "Name"
                and get(value, "id", default=None) == "self"
            ):
                return True
        return False
