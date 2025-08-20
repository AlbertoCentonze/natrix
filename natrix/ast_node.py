from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable


class Node:
    def __init__(self, node_dict: dict[str, Any], parent: Node | None = None):
        self.node_dict = node_dict
        self.parent = parent
        self.children: list[Node] = []
        self._cache_descendants: list[Node] | None = None

        self._build_children()

    @classmethod
    def from_dict(cls, node_dict: dict[str, Any], parent: Node | None = None) -> Node:
        """
        Factory method that decides which subclass to instantiate
        based on the AST node type.
        """
        ast_type = node_dict.get("ast_type")
        if ast_type == "FunctionDef":
            return FunctionDefNode(node_dict, parent=parent)
        elif ast_type == "Module":
            return ModuleNode(node_dict, parent=parent)
        return cls(node_dict, parent=parent)

    def _build_children(self) -> None:
        for _, value in self.node_dict.items():
            if isinstance(value, dict) and "ast_type" in value:
                child_node = Node.from_dict(value, parent=self)
                self.children.append(child_node)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and "ast_type" in item:
                        child_node = Node.from_dict(item, parent=self)
                        self.children.append(child_node)

    @cached_property
    def ast_type(self) -> str | None:
        value = self.get("ast_type")
        return value if isinstance(value, str) else None

    def __repr__(self) -> str:
        match self.ast_type:
            case None:
                raise ValueError("Node does not have an 'ast_type' attribute.")
            case "Name":
                return f"<Name {self.get('id')}>"
            case "Assign":
                return f"<{self.get('target.attr')} = {self.get('value.attr')}>"
            case "AnnAssign":
                return f"<{self.get('target.id')} = {self.get('value.value')}>"
            case _:
                return f"<Node {self.ast_type}>"

    def get_ancestor(
        self, node_type: str | tuple[str, ...] | None = None
    ) -> Node | None:
        """
        Return an ancestor node for this node.
        If `node_type` is given, finds the first ancestor whose `ast_type`
        is that value.
        """
        if node_type is None or self.parent is None:
            return self.parent

        if isinstance(node_type, str):
            node_type = (node_type,)

        if self.parent.ast_type in node_type:
            return self.parent

        return self.parent.get_ancestor(node_type)

    def get_children(
        self,
        node_type: str | tuple[str, ...] | None = None,
        filters: dict[str, Any] | None = None,
        reverse: bool = False,
    ) -> list[Node]:
        """
        Return immediate children matching the given type/filters.
        """
        return _apply_filters(iter(self.children), node_type, filters, reverse)

    def get_descendants(
        self,
        node_type: str | tuple[str, ...] | None = None,
        filters: dict[str, Any] | None = None,
        include_self: bool = False,
        reverse: bool = False,
    ) -> list[Node]:
        """
        Return all descendants matching the given type/filters.

        A descendant is any node which exists within the AST beneath the given node.
        """
        ret = self._get_descendants(include_self)
        return _apply_filters(ret, node_type, filters, reverse)

    def _get_descendants(self, include_self: bool = True) -> list[Node]:
        if self._cache_descendants is None:
            nodes = []
            if include_self:
                nodes.append(self)
            for child in self.children:
                nodes.extend(child._get_descendants(include_self=True))
            self._cache_descendants = nodes
        if self._cache_descendants is None:
            return []
        return self._cache_descendants

    def get(self, field_str: str, default: Any = None) -> Any:
        """
        Safely retrieve nested properties from `node_dict`.
        `field_str` may include dots to retrieve nested keys.
        """
        obj = self.node_dict
        for key in field_str.split("."):
            if isinstance(obj, dict):
                obj = obj.get(key, default)
            else:
                return default
            if obj is None:
                return default
        return obj

    @cached_property
    def module_node(self) -> Node:
        """
        Get the root module node from any node in the AST.
        """
        module_node = self
        while module_node.parent is not None:
            module_node = module_node.parent
        return module_node

    @cached_property
    def immutable_vars(self) -> set[str]:
        """
        Get all immutable variables from the module.

        Returns:
            set: A set of variable names that are declared as immutable.
        """
        # Find all variable declarations in the module
        var_decls = self.module_node.get_descendants(node_type="VariableDecl")

        # Extract immutable variables
        immutable_vars = set()
        for decl in var_decls:
            if decl.get("is_immutable") is True:
                var_name = decl.get("target.id")
                if var_name:
                    immutable_vars.add(var_name)

        return immutable_vars


@dataclass()
class MemoryAccess:
    node: Node
    type: str  # "read" or "write"
    var: str


class ModuleNode(Node):
    """
    Specialized AST Node subclass for Module nodes.
    Contains properties for call graph generation.
    """

    @cached_property
    def functions(self) -> list[FunctionDefNode]:
        """
        Returns all FunctionDef nodes in this module.
        """
        nodes = self.get_descendants(node_type="FunctionDef")
        return [node for node in nodes if isinstance(node, FunctionDefNode)]

    @cached_property
    def call_graph(self) -> dict[str, list[str]]:
        """
        Returns a dictionary mapping function names to their called functions.
        """
        graph = {}
        for func in self.functions:
            func_name = func.get("name")
            if func_name:
                graph[func_name] = func.called_functions

        return graph


class FunctionDefNode(Node):
    """
    Specialized AST Node subclass for FunctionDef nodes.
    Contains properties and logic specific to functions.
    """

    @cached_property
    def is_constructor(self) -> bool:
        return self.ast_type == "FunctionDef" and self.get("name") == "__init__"

    @cached_property
    def is_from_interface(self) -> bool:
        # Checks if the parent node is an InterfaceDef
        return (self.parent is not None) and (self.parent.ast_type == "InterfaceDef")

    @cached_property
    def modifiers(self) -> list[str]:
        """
        Return a list of Vyper decorators (e.g. "view", "pure", "external")
        found on this function.
        """
        # The compiler attaches them in the "decorator_list" as an array
        # of e.g. {'id': 'view'}
        return [
            decorator["id"]
            for decorator in self.get("decorator_list", default=[])
            if "id" in decorator
        ]

    @cached_property
    def is_runtime_code(self) -> bool:
        return not (self.is_constructor or self.is_from_interface)

    @cached_property
    def is_external(self) -> bool:
        """
        Check if the function is external by looking for the 'external' modifier.
        """
        return "external" in self.modifiers

    @cached_property
    def is_internal(self) -> bool:
        """
        Check if the function is internal by looking for the 'internal' modifier.
        """
        return "internal" in self.modifiers or not (
            "external" in self.modifiers or self.is_runtime_code
        )

    @cached_property
    def memory_accesses(self) -> list[MemoryAccess]:
        """
        Returns all storage read/write accesses inside this function by scanning for
        variable_reads/variable_writes in nodes. Excludes function arguments which
        are read from calldata, not storage.
        """
        # Get all nodes that might have variable_reads or variable_writes
        all_nodes = self.get_descendants()
        if not all_nodes:
            return []

        accesses: list[MemoryAccess] = []

        for node in all_nodes:
            for access_type in ("variable_reads", "variable_writes"):
                if access_type in node.node_dict:
                    for item in node.get(access_type):
                        # Only include storage accesses (accessed via self.variable)
                        # Check if this is an Attribute node where value.id is 'self'
                        # This automatically excludes:
                        # - Function arguments (accessed directly as Name nodes)
                        # - Local variables (accessed directly as Name nodes)
                        if (
                            node.ast_type == "Attribute"
                            and node.node_dict.get("value", {}).get("id") == "self"
                        ):
                            accesses.append(
                                MemoryAccess(
                                    node=node,
                                    type="read"
                                    if access_type == "variable_reads"
                                    else "write",
                                    var=item.get("name"),
                                )
                            )
        return accesses

    @cached_property
    def called_functions(self) -> list[str]:
        """
        Returns a list of unique function names that this function calls.
        """
        # Get all Call nodes within this function
        call_nodes = self.get_descendants(node_type="Call")
        called_funcs = []

        for call in call_nodes:
            func_attr = call.get("func.attr")
            if func_attr:
                # Check if there's an object/module before the method
                func_value_id = call.get("func.value.id")
                if func_value_id and func_value_id != "self":
                    # Include the object/module name (e.g., AMM.withdraw)
                    called_funcs.append(f"{func_value_id}.{func_attr}")
                else:
                    # Just the function name for self calls
                    called_funcs.append(func_attr)

        # Return unique calls to avoid duplicate edges
        return list(dict.fromkeys(called_funcs))

    def __repr__(self) -> str:
        return f"<FunctionDef {self.get('name')}>"


def _apply_filters(
    iterable: Iterable[Node],
    node_type: str | tuple[str, ...] | None = None,
    filters: dict[str, Any] | None = None,
    reverse: bool = False,
) -> list[Node]:
    """
    Generic filtering utility for Node lists.
    """
    if node_type is not None and isinstance(node_type, str):
        node_type = (node_type,)

    results = []
    for node in iterable:
        if node_type and node.ast_type not in node_type:
            continue

        if filters:
            match = True
            for attr_name, expected_value in filters.items():
                attr_value = node.get(attr_name)
                if isinstance(expected_value, set):
                    if attr_value not in expected_value:
                        match = False
                        break
                else:
                    if attr_value != expected_value:
                        match = False
                        break
            if not match:
                continue

        results.append(node)

    if reverse:
        results.reverse()

    return results
