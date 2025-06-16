from __future__ import annotations

import ast
import json
import re
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from natrix.ast_node import Node

VYPER_VERSION = "0.4.2"


def _check_vyper_version() -> None:
    """
    Check if vyper is installed and at the required version.
    Raises an exception if vyper is not available or not at the correct version.
    """
    try:
        result = subprocess.run(["vyper", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception("Vyper compiler not available")

        # Extract version number
        version_match = re.search(r"(\d+\.\d+\.\d+)", result.stdout)
        if not version_match:
            raise Exception("Could not determine Vyper version")

        version = version_match.group(1)
        if version != VYPER_VERSION:
            raise Exception(f"Vyper version must be {VYPER_VERSION}, found {version}")
    except FileNotFoundError as e:
        raise Exception(
            f"Vyper compiler not found. Please ensure Vyper {VYPER_VERSION} "
            "is installed and available in your PATH."
        ) from e


def _obtain_sys_path() -> list[str]:
    """
    Obtain all the system paths in which the compiler would
    normally look for modules. This allows to lint vyper files
    that import a module that is installed as a virtual environment
    dependency.
    """
    command = ["python", "-c", "import sys; print(sys.path)"]

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout, stderr = process.communicate()

    # Remove the first element of the list which is an empty string.
    paths = ast.literal_eval(stdout)[1:]

    # Remove paths that do not exist as the vyper compiler will throw an error.
    valid_paths = [path for path in paths if Path(path).exists()]

    return valid_paths


def _obtain_default_paths() -> list[str]:
    """
    Obtain default paths for Vyper imports.
    Only returns paths that actually exist on the system.
    """
    # List of default paths to check
    default_paths = [
        "lib/pypi",  # Default dependency folder for moccasin
        # Add more paths here in the future
    ]

    # Return only existing paths
    existing_paths = []
    for path in default_paths:
        path_obj = Path(path)
        if path_obj.exists() and path_obj.is_dir():
            existing_paths.append(path)

    return existing_paths


def vyper_compile(
    filename: str, formatting: str, extra_paths: tuple[str, ...] = ()
) -> dict[str, Any] | list[dict[str, Any]]:
    _check_vyper_version()

    # Combine all paths
    all_paths = _obtain_sys_path() + _obtain_default_paths() + list(extra_paths)

    # Convert to compiler flags
    path_flags = [item for p in all_paths for item in ["-p", p]]

    command = ["vyper", "-f", formatting, filename, *path_flags]

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout, stderr = process.communicate()

    try:
        result = json.loads(stdout)
        # Assert that result is either dict or list to satisfy mypy
        assert isinstance(result, dict | list)
        return result
    except Exception as e:
        # TODO change error level
        raise Exception(
            f"Something went wrong when compiling the vyper file '{filename}'. "
            f"The compiler returned the following error: \n {stderr}"
        ) from e


def parse_file(file_path: str, extra_paths: tuple[str, ...] = ()) -> dict[str, Any]:
    ast = vyper_compile(file_path, "annotated_ast", extra_paths=extra_paths)
    # For annotated_ast, vyper_compile returns a dict
    assert isinstance(ast, dict)

    # Try to compile metadata, but handle InitializerException gracefully
    # This happens when a module uses deferred initialization (uses: module_name)
    try:
        metadata = vyper_compile(file_path, "metadata", extra_paths=extra_paths)
        # For metadata, vyper_compile also returns a dict
        assert isinstance(metadata, dict)
        ast["metadata"] = metadata
    except Exception as e:
        error_str = str(e)
        if (
            "vyper.exceptions.InitializerException" in error_str
            and "is used but never initialized!" in error_str
        ):
            # Skip metadata for files with deferred module initialization
            # This is a known limitation of the Vyper compiler
            pass
        else:
            # Re-raise other exceptions
            raise e

    return ast


def parse_source(source_code: str) -> dict[str, Any]:
    """
    Parse Vyper source code directly without requiring a file path.

    Args:
        source_code: The Vyper source code as a string

    Returns:
        The parsed AST with metadata
    """
    import tempfile

    # Create a temporary file to hold the source code
    with tempfile.NamedTemporaryFile(mode="w", suffix=".vy", delete=False) as temp_file:
        temp_file.write(source_code)
        temp_file_path = temp_file.name

    try:
        # Parse the temporary file
        result = parse_file(temp_file_path)
        return result
    finally:
        # Clean up the temporary file
        Path(temp_file_path).unlink()


class VyperASTVisitor:
    def visit(self, node: Node) -> None:
        ast_type = node.ast_type
        if ast_type:
            method_name = f"visit_{ast_type}"
            visitor = getattr(self, method_name, None)
            if visitor:
                visitor(node)

        if node.children:
            for child in node.children:
                self.visit(child)
