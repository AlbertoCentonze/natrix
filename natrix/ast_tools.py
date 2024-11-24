import dpath
import subprocess
import json


def vyper_compile(filename, formatting):
    command = ["uvx", "vyper@0.4.0", "-f", formatting, filename]

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout, stderr = process.communicate()

    return json.loads(stdout)


def parse_file(file_path):
    ast = vyper_compile(file_path, "annotated_ast")
    metadata = vyper_compile(file_path, "metadata")

    ast["metadata"] = metadata
    return ast


class VyperASTVisitor:
    def visit(self, node):
        if isinstance(node, dict):
            ast_type = get(node, "ast_type")
            if ast_type:
                method_name = f"visit_{ast_type}"
                visitor = getattr(self, method_name, self.generic_visit)
                return visitor(node)
            else:
                return self.generic_visit(node)
        elif isinstance(node, list):
            for item in node:
                self.visit(item)

    def generic_visit(self, node):
        # Recursively visit all child nodes
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                self.visit(value)


def is_constructor(node):
    return (
        isinstance(node, dict)
        and get(node, "ast_type") == "FunctionDef"
        and get(node, "name") == "__init__"
    )


def get(node, field_str, default=None):
    """
    Recursive getter function for node attributes.

    Parameters
    ----------
    node : dict
        The current node in the AST.
    field_str : str
        Attribute string of the location of the node to return.
    default: Any, optional
        Default value to return if the field string is invalid.

    Returns
    -------
    Any
        Value at the location of the given field string, if one
        exists. `None` if the field string is empty or invalid.
    """
    return dpath.get(node, field_str, default=default, separator=".")


def _apply_filters(nodes, node_type=None, filters=None, reverse=False):
    """
    Apply node_type and filters to a list of nodes.

    Parameters
    ----------
    nodes : list
        List of nodes to filter.
    node_type : str or tuple of str, optional
        A node type or tuple of types.
    filters : dict, optional
        Dictionary of attribute names and expected values.
    reverse : bool, optional
        If `True`, the order of results is reversed prior to return.

    Returns
    -------
    list
        Nodes matching the filter conditions.
    """
    # Apply node_type filter
    if node_type is not None:
        if isinstance(node_type, tuple):
            node_types = node_type
        else:
            node_types = (node_type,)
        nodes = [n for n in nodes if n.get("ast_type") in node_types]

    # Apply filters
    if filters:
        filtered_nodes = []
        for n in nodes:
            is_match = True
            for key, expected in filters.items():
                value = get(n, key)
                if isinstance(expected, set):
                    if value not in expected:
                        is_match = False
                        break
                else:
                    if value != expected:
                        is_match = False
                        break
            if is_match:
                filtered_nodes.append(n)
        nodes = filtered_nodes

    if reverse:
        nodes.reverse()
    return nodes


def get_children(node, node_type=None, filters=None, reverse=False):
    """
    Return a list of children of this node which match the given filter(s).

    Parameters
    ----------
    node : dict
        The current node in the AST.
    node_type : str or tuple of str, optional
        A node type or tuple of types. If given, only child nodes where the
        type matches this value are returned.
    filters : dict, optional
        Dictionary of attribute names and expected values. Only nodes that
        contain the given attributes and match the given values are returned.
        * Use dots within the name to check nested attributes.
          e.g. `{'value.id': "owner"}`
        * Expected values may be given as a set. To match, a node must
          contain the given attribute and match any one value within the set.
          e.g. `{'id': {'public', 'constant'}}` matches nodes with an `id`
                attribute that is either "public" or "constant".
    reverse : bool, optional
        If `True`, the order of results is reversed prior to return.

    Returns
    -------
    list
        Child nodes matching the filter conditions.
    """
    # Collect immediate child nodes
    children = []
    for key, value in node.items():
        if isinstance(value, dict) and "ast_type" in value:
            children.append(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and "ast_type" in item:
                    children.append(item)

    # Apply filters using the helper function
    return _apply_filters(children, node_type, filters, reverse)


def get_descendants(
    node, node_type=None, filters=None, include_self=False, reverse=False
):
    """
    Return a list of descendant nodes of this node which match the given filter(s).

    A descendant is any node which exists within the AST beneath the given node.

    Parameters
    ----------
    node : dict
        The current node in the AST.
    node_type : str or tuple of str, optional
        A node type or tuple of types. If given, only descendant nodes where the
        type matches this value are returned.
    filters : dict, optional
        Dictionary of attribute names and expected values. Only nodes that
        contain the given attributes and match the given values are returned.
        * Use dots within the name to check nested attributes.
          e.g. `{'value.id': "owner"}`
        * Expected values may be given as a set. To match, a node must
          contain the given attribute and match any one value within the set.
          e.g. `{'id': {'public', 'constant'}}` matches nodes with an `id`
                attribute that is either "public" or "constant".
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
    descendants = []

    def traverse(n):
        if include_self or n != node:
            descendants.append(n)
        for child in get_children(n):
            traverse(child)

    traverse(node)

    # Apply filters using the helper function
    return _apply_filters(descendants, node_type, filters, reverse)
