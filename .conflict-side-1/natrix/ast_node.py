from dataclasses import dataclass
from functools import cached_property
from typing import List


class Node:
    def __init__(self, node_dict: dict, parent=None):
        self.node_dict = node_dict
        self.parent = parent
        self.children: List[Node] = []
        self._cache_descendants = None

        self._build_children()

    @classmethod
    def from_dict(cls, node_dict: dict, parent=None) -> "Node":
        """
        Factory method that decides which subclass to instantiate
        based on the AST node type.
        """
        ast_type = node_dict.get("ast_type")
        if ast_type == "FunctionDef":
            return FunctionDefNode(node_dict, parent=parent)
        return cls(node_dict, parent=parent)

    def _build_children(self):
        for key, value in self.node_dict.items():
            if isinstance(value, dict) and "ast_type" in value:
                child_node = Node.from_dict(value, parent=self)
                self.children.append(child_node)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and "ast_type" in item:
                        child_node = Node.from_dict(item, parent=self)
                        self.children.append(child_node)

    @cached_property
    def ast_type(self):
        return self.get("ast_type")

    def __repr__(self):
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

    def get_ancestor(self, node_type=None) -> "Node | None":
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

    def get_children(self, node_type=None, filters=None, reverse=False) -> List["Node"]:
        """
        Return immediate children matching the given type/filters.
        """
        return _apply_filters(iter(self.children), node_type, filters, reverse)

    def get_descendants(
        self, node_type=None, filters=None, include_self=False, reverse=False
    ) -> List["Node"]:
        """
        Return all descendants matching the given type/filters.

        A descendant is any node which exists within the AST beneath the given node.
        """
        ret = self._get_descendants(include_self)
        return _apply_filters(ret, node_type, filters, reverse)

    def _get_descendants(self, include_self=True) -> List["Node"]:
        if self._cache_descendants is None:
            nodes = []
            if include_self:
                nodes.append(self)
            for child in self.children:
                nodes.extend(child._get_descendants(include_self=True))
            self._cache_descendants = nodes
        return self._cache_descendants

    def get(self, field_str, default=None):
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


@dataclass()
class MemoryAccess:
    node: Node
    type: str  # "read" or "write"
    var: str


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
    def modifiers(self) -> List[str]:
        """
        Return a list of Vyper decorators (e.g. "view", "pure", "external") found on this function.
        """
        # The compiler attaches them in the "decorator_list" as an array of e.g. {'id': 'view'}
        return [
            decorator["id"]
            for decorator in self.get("decorator_list", default=[])
            if "id" in decorator
        ]

    @cached_property
    def memory_accesses(self) -> List[MemoryAccess]:
        """
        Returns all read/write accesses inside this function by scanning for
        variable_reads/variable_writes in nodes.
        """
        # If the node is not actually a FunctionDef, raise:
        if self.ast_type != "FunctionDef":
            raise ValueError("Not a function")

        attrs = self.get_descendants("Attribute")
        if not attrs:
            return []

        accesses: List[MemoryAccess] = []

        for attr in attrs:
            for access_type in ("variable_reads", "variable_writes"):
                if access_type in attr.node_dict:
                    for item in attr.get(access_type):
                        accesses.append(
                            MemoryAccess(
                                node=attr,
                                type="read"
                                if access_type == "variable_reads"
                                else "write",
                                var=item.get("name"),
                            )
                        )
        return accesses

    def __repr__(self):
        return f"<FunctionDef {self.get('name')}>"


def _apply_filters(iterable, node_type=None, filters=None, reverse=False) -> List[Node]:
    """
    Generic filtering utility for Node lists.
    """
    if node_type is not None:
        if isinstance(node_type, str):
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
