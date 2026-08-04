from __future__ import annotations

from natrix.ast_node import FunctionDefNode, ModuleNode, Node
from natrix.rules.common import BaseRule, RuleRegistry


@RuleRegistry.register
class NonViewReadsStateRule(BaseRule):
    """
    Non-view Function Reads State
    Non-view functions should not read contract state unless they are modifying it.
    """

    CODE = "NTX4"
    MESSAGE = "Function '{}' reads contract state but is not marked as 'view'."

    def visit_FunctionDef(self, node: FunctionDefNode) -> None:
        # Get all state reads
        state_reads = []
        for access in node.memory_accesses:
            if access.type == "read" and access.var.startswith("self."):
                state_reads.append(access)

        # If no state reads, nothing to flag
        if not state_reads:
            return

        # Check if function has view modifier
        if any(mod.get("id") == "view" for mod in node.get("decorator_list", [])):
            return

        # If function has extcall statements, it's modifying state
        for stmt in node.get("body", []):
            if isinstance(stmt, dict) and stmt.get("ast_type") == "ExtCall":
                return

        # Get module info to access call graph
        module_info = self.context.get_module(self.file_path)
        if module_info is None:
            return
        module_node = Node(module_info.compiler_output)
        if not isinstance(module_node, ModuleNode):
            module_node = ModuleNode(module_node.node_dict, parent=module_node.parent)

        # Get all functions in this module
        all_funcs = {func.get("name"): func for func in module_node.functions}

        # Check if function calls any internal function without view modifier
        # If so, it's implicitly modifying state through that call
        for called_func in node.called_functions:
            # Extract function name (handle dotted names like "module.func")
            called_func_name = called_func.split(".")[-1]

            # Check if called_func is an internal function in this module
            if called_func_name in all_funcs:
                called_func_node = all_funcs[called_func_name]
                # Check if called function has view modifier
                has_view = any(
                    mod.get("id") == "view"
                    for mod in called_func_node.get("decorator_list", [])
                )
                if not has_view:
                    # Called function is not view, so this function modifies state
                    return

        # Function reads state, is not view, and doesn't modify state through calls
        # This is the violation
        self.add_issue(node, node.get("name"))
