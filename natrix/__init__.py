import sys
import os
import argparse
import inspect

# Import tomllib for Python 3.11+ or tomli for earlier versions
try:
    import tomllib
except ImportError:
    import tomli as tomllib

from natrix.__version__ import __version__
from natrix.rules import rules
from natrix.ast_tools import parse_file


def lint_file(file_path):
    ast = parse_file(file_path)

    # flatmaps the issues from all rules
    issues = [issue for rule in rules for issue in rule.run(ast)]

    for issue in issues:
        print(issue.cli_format())

    return bool(issues)


def find_vy_files(directory):
    # Recursively find all .vy files in the given directory, excluding specified directories
    vy_files = []
    for root, dirs, files in os.walk(directory):
        # Collect all .vy files
        for file in files:
            if file.endswith(".vy"):
                vy_files.append(os.path.join(root, file))

    return vy_files


def get_project_root():
    """Get the project root directory, which contains the pyproject.toml file."""
    # First try to find it from the current working directory upwards
    current_dir = os.path.abspath(os.getcwd())
    while current_dir != os.path.dirname(current_dir):  # Stop at root directory
        if os.path.exists(os.path.join(current_dir, "pyproject.toml")):
            return current_dir
        current_dir = os.path.dirname(current_dir)

    # If not found, try to find it based on the module directory
    module_dir = os.path.dirname(
        os.path.abspath(inspect.getfile(inspect.currentframe()))
    )
    root_dir = os.path.dirname(module_dir)  # Go one level up from the module directory
    if os.path.exists(os.path.join(root_dir, "pyproject.toml")):
        return root_dir

    # If still not found, return the current directory as a fallback
    return os.getcwd()


def read_pyproject_config():
    """Read configurations from pyproject.toml if it exists"""
    config = {"files": []}

    try:
        # Find the project root directory
        project_root = get_project_root()
        pyproject_path = os.path.join(project_root, "pyproject.toml")

        if os.path.exists(pyproject_path):
            with open(pyproject_path, "rb") as f:
                pyproject = tomllib.load(f)
                if "tool" in pyproject and "natrix" in pyproject["tool"]:
                    natrix_config = pyproject["tool"]["natrix"]
                    if "files" in natrix_config and isinstance(
                        natrix_config["files"], list
                    ):
                        # Make paths relative to pyproject.toml location
                        config["files"] = [
                            os.path.normpath(os.path.join(project_root, path))
                            for path in natrix_config["files"]
                        ]
    except Exception as e:
        print(f"Warning: Error reading pyproject.toml: {e}")

    return config


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="A linter for Vyper Smart Contracts.")
    parser.add_argument(
        "files",
        nargs="*",
        help="Path(s) to vyper file(s) or directory/directories to lint. If not provided, all vyper files in current directory are checked.",
    )
    parser.add_argument("--version", action="store_true", help="Show version and exit.")
    return parser.parse_args()


def main():
    args = parse_args()
    config = read_pyproject_config()
    issues_found = False

    if args.version:
        print(__version__)
        sys.exit(0)

    files_to_check = args.files

    # If no command-line files specified, use files from pyproject.toml
    if not files_to_check and config["files"]:
        files_to_check = config["files"]

    if files_to_check:
        all_vy_files = []
        for path in files_to_check:
            if os.path.isfile(path) and path.endswith(".vy"):
                # If a specific .vy file is provided
                all_vy_files.append(path)
            elif os.path.isdir(path):
                # If a directory is provided, find all .vy files in it
                dir_vy_files = find_vy_files(path)
                if not dir_vy_files:
                    print(f"No .vy files found in the directory: {path}")
                all_vy_files.extend(dir_vy_files)
            else:
                print(f"Provided path is not a valid .vy file or directory: {path}")

        if not all_vy_files:
            print("No valid .vy files to lint.")
            sys.exit(1)

        issues = [lint_file(file) for file in all_vy_files]
        issues_found = any(issues)
    else:
        # If no paths are provided, search for .vy files in the current directory recursively
        vy_files = find_vy_files(".")

        if not vy_files:
            print("No .vy files found in the current directory.")
            sys.exit(1)

        issues = [lint_file(file) for file in vy_files]
        issues_found = any(issues)

    if issues_found:
        sys.exit(1)
    else:
        print("Vyper files are lint free! 🐍")
        sys.exit(0)


if __name__ == "__main__":
    main()
