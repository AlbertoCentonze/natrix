from functools import cached_property
from typing import List


class Node:
    def __init__(self, node_dict: dict, parent=None):
        self.node_dict = node_dict
        self.parent = parent
        self.children: List[Node] = []
        self._cache_descendants = None

        # Build children nodes
        self._build_children()

    def _build_children(self):
        for key, value in self.node_dict.items():
            if isinstance(value, dict) and "ast_type" in value:
                child_node = Node(value, parent=self)
                self.children.append(child_node)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and "ast_type" in item:
                        child_node = Node(item, parent=self)
                        self.children.append(child_node)

    @cached_property
    def ast_type(self):
        return self.get("ast_type")

    @cached_property
    def is_constructor(self):
        return self.ast_type == "FunctionDef" and self.get("name") == "__init__"

    @cached_property
    def is_from_interface(self) -> bool:
        # TODO not a big fan of this property, should be in parent
        return self.parent.ast_type == "InterfaceDef"

    @cached_property
    def modifiers(self) -> List[str]:
        # !! this function only returns modifiers that are explicit
        # !! in the source contract
        if self.ast_type != "FunctionDef":
            raise ValueError(
                "Node type is not a FunctionDef so it can't have modifiers"
            )
        return [decorator["id"] for decorator in self.get("decorator_list")]

    def __repr__(self):
        match self.ast_type:
            case None:
                raise ValueError("Node does not have an 'ast_type' attribute.")
            case "Name":
                return f"<Name {self.get('id')}>"
            case "FunctionDef":
                return f"<FunctionDef {self.get('name')}>"
            case "Assign":
                return f"<{self.get('target.attr')} = {self.get('value.attr')}>"
            case "AnnAssign":
                return f"<{self.get('target.id')} = {self.get('value.value')}>"
            # case "AugAssign":
            # return f"<{}>"
            case _:
                return f"<Node {self.ast_type}>"

    def get_ancestor(self, node_type=None) -> "Node":
        """
        Return an ancestor node for this node.

        An ancestor is any node which exists within the AST above the given node.

        Parameters
        ----------
        node_type : str | tuple, optional
            A node type or tuple of types. If given, this method checks all
            ancestor nodes of this node starting with the parent, and returns
            the first node with a type matching the given value.

        Returns
        -------
        Node or None
            With no arguments given: the parent of this node.
            With `node_type`: the first matching ancestor node, or `None` if no node
            is found which matches the argument value.
        """
        if node_type is None or self.parent is None:
            return self.parent

        if isinstance(node_type, str):
            node_type = (node_type,)

        if self.parent.ast_type in node_type:
            return self.parent

        return self.parent.get_ancestor(node_type)

    def get_children(self, node_type=None, filters=None, reverse=False):
        """
        Return a list of children of this node which match the given filter(s).

        Parameters
        ----------
        node_type : str | tuple, optional
            A node type or tuple of types. If given, only child nodes where the
            `ast_type` matches this value are returned.
        filters : dict, optional
            Dictionary of attribute names and expected values. Only nodes that
            contain the given attributes and match the given values are returned.
            * You can use dots within the name to check nested attributes.
              e.g. `{'annotation.func.id': "constant"}`
            * Expected values may be given as a set; the node must match any one
              value within the set.
        reverse : bool, optional
            If `True`, the order of results is reversed prior to return.

        Returns
        -------
        list
            Child nodes matching the filter conditions.
        """
        return _apply_filters(iter(self.children), node_type, filters, reverse)

    def get_descendants(
        self, node_type=None, filters=None, include_self=False, reverse=False
    ) -> List["Node"]:
        """
        Return a list of descendant nodes of this node which match the given filter(s).

        A descendant is any node which exists within the AST beneath the given node.

        Parameters
        ----------
        node_type : str | tuple, optional
            A node type or tuple of types. If given, only descendant nodes where the
            `ast_type` matches this value are returned.
        filters : dict, optional
            Dictionary of attribute names and expected values. Only nodes that
            contain the given attributes and match the given values are returned.
            * You can use dots within the name to check nested attributes.
            * Expected values may be given as a set; the node must match any one
              value within the set.
        include_self : bool, optional
            If True, this node is also included in the search results if it matches
            the given filter.
        reverse : bool, optional
            If `True`, the order of results is reversed prior to return.

        Returns
        -------
        list
            Descendant nodes matching the filter conditions.
        """
        ret = self._get_descendants(include_self)
        return _apply_filters(ret, node_type, filters, reverse)

    def _get_descendants(self, include_self=True):
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
        Recursive getter function for node attributes.

        Parameters
        ----------
        field_str : str
            Attribute string of the location of the value to return.

        Returns
        -------
        Any
            Value at the location of the given field string, if one exists.
            `None` if the field string is empty or invalid.
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


def _apply_filters(iterable, node_type=None, filters=None, reverse=False):
    """
    Filter the given iterable of nodes based on node_type and filters.

    Parameters
    ----------
    iterable : iterator
        An iterator of Node instances.
    node_type : str | tuple, optional
        A node type or tuple of types. If given, only nodes where the
        `ast_type` matches this value are included.
    filters : dict, optional
        Dictionary of attribute names and expected values. Only nodes that
        contain the given attributes and match the given values are included.
    reverse : bool, optional
        If `True`, the order of results is reversed prior to return.

    Returns
    -------
    list
        Nodes that match the given criteria.
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
