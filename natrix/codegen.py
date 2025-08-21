"""Code generation functionality for Natrix."""

from pathlib import Path

from natrix.ast_node import ModuleNode, Node
from natrix.ast_tools import vyper_compile


def generate_exports(
    file_path: Path,
    extra_paths: tuple[Path, ...],
    include_module_comments: bool = False,
) -> str:
    """Generate explicit exports for a Vyper contract.

    Args:
        file_path: Path to the Vyper contract file
        extra_paths: Additional paths to search for imports
        include_module_comments: Whether to include comments
        showing which module functions come from

    Returns:
        A string containing the exports declaration
    """
    # Extract module name from file path
    module_name = file_path.stem

    # Get the ABI from vyper
    abi = vyper_compile(file_path, "abi", extra_paths=extra_paths)
    # For abi format, vyper_compile returns a list
    assert isinstance(abi, list)

    # Extract function names from ABI (use a set to avoid duplicates)
    external_funcs: set[str] = set()
    for item in abi:
        if item["type"] == "function":
            external_funcs.add(item["name"])

    # Convert to sorted list for deterministic output
    external_funcs_list = sorted(external_funcs)

    # If module comments are requested, parse AST to get module mapping
    func_to_module: dict[str, str] = {}
    if include_module_comments and external_funcs_list:
        func_to_module = _get_function_to_module_mapping(file_path, extra_paths)

    # Format the exports
    if external_funcs_list:
        func_list = []
        for i, func in enumerate(external_funcs_list):
            func_line = f"    {module_name}.{func}"

            # Add comma to all items except the last one
            if i < len(external_funcs_list) - 1:
                func_line += ","

            # Add module comment if available
            if include_module_comments and func in func_to_module:
                func_line += f"  # {func_to_module[func]}"

            func_list.append(func_line)

        func_names = "\n".join(func_list)
        return (
            f"# NOTE: Always double-check the generated exports\n"
            f"exports: (\n{func_names}\n)"
        )
    else:
        return f"# No external functions found in {module_name}"


def _get_function_to_module_mapping(
    file_path: Path, extra_paths: tuple[Path, ...]
) -> dict[str, str]:
    """Parse the AST to map function names to their source modules.

    Args:
        file_path: Path to the Vyper contract file
        extra_paths: Additional paths to search for imports

    Returns:
        A dictionary mapping function names to their source module names
    """
    # Get the annotated AST from vyper
    full_dict = vyper_compile(file_path, "annotated_ast", extra_paths=extra_paths)
    assert isinstance(full_dict, dict)

    func_to_module: dict[str, str] = {}

    # Extract imported modules and their function names
    imports = full_dict.get("imports", [])
    for import_dict in imports:
        if "path" in import_dict and "body" in import_dict:
            # Extract module name from path
            import_path = import_dict["path"]
            module_name = Path(import_path).stem

            # Look through the imported module's AST body
            # for function definitions and public variables
            for node in import_dict["body"]:
                if node.get("ast_type") == "FunctionDef":
                    func_name = node.get("name")
                    if func_name:
                        func_to_module[func_name] = module_name
                elif node.get("ast_type") == "VariableDecl" and node.get("is_public"):
                    # Public variables generate getter functions
                    var_name = node.get("target", {}).get("id")
                    if var_name:
                        func_to_module[var_name] = module_name

    return func_to_module


def generate_call_graph(
    file_path: Path, extra_paths: tuple[Path, ...], target_function: str | None = None
) -> str:
    """Generate a Mermaid call graph for a Vyper contract.

    Args:
        file_path: Path to the Vyper contract file
        extra_paths: Additional paths to search for imports
        target_function: Optional specific function to generate call graph for

    Returns:
        A string containing the Mermaid diagram
    """
    # Get the annotated AST from vyper
    full_dict = vyper_compile(file_path, "annotated_ast", extra_paths=extra_paths)
    assert isinstance(full_dict, dict)
    ast_dict = full_dict.get("ast", full_dict)  # Extract the 'ast' key if present

    # Create the AST node tree
    root = Node.from_dict(ast_dict)
    assert isinstance(root, ModuleNode)

    # Get the full call graph
    full_call_graph = root.call_graph

    # Filter for specific function if requested
    if target_function:
        # Build a graph starting from the target function
        call_graph = {}
        visited = set()

        def collect_calls(func_name: str) -> None:
            if func_name in visited or func_name not in full_call_graph:
                return
            visited.add(func_name)
            calls = full_call_graph.get(func_name, [])
            call_graph[func_name] = calls
            for called in calls:
                collect_calls(called)

        collect_calls(target_function)
    else:
        call_graph = full_call_graph

    # Generate Mermaid diagram
    lines = []

    # Calculate dynamic rank spacing based on number of nodes
    all_funcs = set(call_graph.keys())
    for calls in call_graph.values():
        all_funcs.update(calls)
    node_count = len(all_funcs)

    # Scale rank spacing with node count (base 150, +10 per node, max 800)
    rank_spacing = min(150 + node_count * 10, 800)

    # Add init configuration
    lines.extend(
        [
            "%%{init: {",
            '  "flowchart": {',
            '    "nodeSpacing": 100,',
            f'    "rankSpacing": {rank_spacing}',
            "  }",
            "}}%%",
            "flowchart TD",
        ]
    )

    # Create a mapping from function names to valid node IDs
    node_id_map = {}
    node_counter = 0

    # Helper to get or create a valid node ID for a function name
    def get_node_id(name: str) -> str:
        nonlocal node_counter
        if name not in node_id_map:
            # Create a simple ID like N0, N1, N2...
            node_id_map[name] = f"N{node_counter}"
            node_counter += 1
        return node_id_map[name]

    # First, declare all nodes with their labels
    all_funcs = set(call_graph.keys())
    for calls in call_graph.values():
        all_funcs.update(calls)

    for func in sorted(all_funcs):
        node_id = get_node_id(func)
        # Use brackets to define node with label
        lines.append(f'    {node_id}["{func}"]')

    # Then add the edges using node IDs
    for func, calls in call_graph.items():
        func_id = get_node_id(func)
        for called in calls:
            called_id = get_node_id(called)
            lines.append(f"    {func_id} --> {called_id}")

    return "\n".join(lines)
