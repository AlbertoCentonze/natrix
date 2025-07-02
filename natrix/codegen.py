"""Code generation functionality for Natrix."""

from pathlib import Path

from natrix.ast_tools import vyper_compile


def generate_exports(file_path: Path, extra_paths: tuple[Path, ...]) -> str:
    """Generate explicit exports for a Vyper contract.

    Args:
        file_path: Path to the Vyper contract file
        extra_paths: Additional paths to search for imports

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

    # Format the exports
    if external_funcs_list:
        func_list = [f"    {module_name}.{func}" for func in external_funcs_list]
        func_names = ",\n".join(func_list)
        return (
            f"# NOTE: Always double-check the generated exports\n"
            f"exports: (\n{func_names}\n)"
        )
    else:
        return f"# No external functions found in {module_name}"
