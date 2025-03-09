import sys
import os
import argparse
import re
from typing import Set

# Import tomllib for Python 3.11+ or tomli for earlier versions
try:
    import tomllib
except ImportError:
    import tomli as tomllib

from natrix.__version__ import __version__
from natrix.ast_tools import parse_file
from natrix.rules.common import RuleRegistry


def lint_file(file_path, disabled_rules: Set[str] = None):
    """Lint a single Vyper file with the given rules configuration."""
    ast = parse_file(file_path)

    if disabled_rules is None:
        disabled_rules = set()

    # Get the rule instances (already instantiated once at startup)
    rules = RuleRegistry.get_rules()

    # flatmaps the issues from all rules and filter out disabled rules
    issues = []
    for rule in rules:
        try:
            rule_issues = rule.run(ast)
            issues.extend(
                [issue for issue in rule_issues if issue.code not in disabled_rules]
            )
        except Exception as e:
            # Simple error message with suggestion to report the issue
            print(
                f"Error running a rule: {str(e)}. Please report this issue on GitHub."
            )

    # Print issues with spacing between them
    for i, issue in enumerate(issues):
        if i > 0:  # Add a blank line between issues
            print()
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

    while current_dir != os.path.dirname(current_dir):  # Stop at root
        if os.path.exists(os.path.join(current_dir, "pyproject.toml")):
            return current_dir
        current_dir = os.path.dirname(current_dir)

    # If not found, default to the current directory
    return os.getcwd()


def read_pyproject_config():
    """Read configurations from pyproject.toml if it exists"""
    config = {"files": [], "disabled_rules": set(), "rule_configs": {}}

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
                    if "disabled_rules" in natrix_config and isinstance(
                        natrix_config["disabled_rules"], list
                    ):
                        config["disabled_rules"] = set(natrix_config["disabled_rules"])
                    # Parse rule configurations
                    if "rule_configs" in natrix_config and isinstance(
                        natrix_config["rule_configs"], dict
                    ):
                        config["rule_configs"] = natrix_config["rule_configs"]
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
    parser.add_argument(
        "-v", "--version", action="store_true", help="Show version and exit."
    )
    parser.add_argument(
        "-d",
        "--disable",
        type=str,
        nargs="+",
        help="List of rule codes to disable (e.g., --disable NTX003 NTX007).",
    )
    parser.add_argument(
        "-c",
        "--rule-config",
        action="append",
        help="Configure rules with format 'RuleName.param=value'. Can be used multiple times. Example: ArgNamingConvention.pattern=^_",
    )
    parser.add_argument(
        "-l",
        "--list-rules",
        action="store_true",
        help="List all available rules with their descriptions.",
    )
    return parser.parse_args()


def main():
    """Main entry point for the linter."""
    args = parse_args()

    if args.version:
        print(f"natrix v{__version__}")
        sys.exit(0)

    # Ensure all rules are discovered
    RuleRegistry.discover_rules()

    if args.list_rules:
        print("Available rules:")
        rule_classes = RuleRegistry.get_rule_classes()
        for rule_name, rule_class in sorted(rule_classes.items()):
            doc = rule_class.__doc__ or ""
            doc_lines = doc.splitlines()
            description = doc_lines[0].strip() if doc_lines else "No description"
            print(f"  {rule_name}: {description}")
        sys.exit(0)

    # Parse rule configurations from CLI
    rule_configs = {}
    if args.rule_config:
        for config_str in args.rule_config:
            try:
                rule_param, value = config_str.split("=", 1)
                rule_name, param = rule_param.split(".", 1)

                # Convert value to appropriate type if possible
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif re.match(r"^\d+\.\d+$", value):
                    value = float(value)

                # Initialize rule configuration dictionary if it doesn't exist
                if rule_name not in rule_configs:
                    rule_configs[rule_name] = {}

                rule_configs[rule_name][param] = value
            except ValueError:
                print(f"Invalid rule configuration format: {config_str}")
                print("Expected format: RuleName.param=value")
                sys.exit(1)

    # Read config from pyproject.toml
    pyproject_config = read_pyproject_config()

    # Merge configurations, with CLI taking precedence
    merged_rule_configs = pyproject_config.get("rule_configs", {}).copy()
    for rule_name, params in rule_configs.items():
        if rule_name not in merged_rule_configs:
            merged_rule_configs[rule_name] = {}
        merged_rule_configs[rule_name].update(params)

    # Initialize rules once with the merged configurations
    RuleRegistry.get_rules(merged_rule_configs)

    # Combine disabled rules from CLI and pyproject.toml
    disabled_rules = pyproject_config["disabled_rules"]
    if args.disable:
        disabled_rules.update(args.disable)

    # Handle files
    if args.files:
        all_vy_files = []
        for path in args.files:
            if os.path.isfile(path) and path.endswith(".vy"):
                all_vy_files.append(path)
            elif os.path.isdir(path):
                dir_vy_files = find_vy_files(path)
                if not dir_vy_files:
                    print(f"No .vy files found in the directory: {path}")
                all_vy_files.extend(dir_vy_files)
            else:
                print(f"Provided path is not a valid .vy file or directory: {path}")

        if not all_vy_files:
            print("No valid .vy files to lint.")
            sys.exit(1)

        issues = [lint_file(file, disabled_rules) for file in all_vy_files]
        issues_found = any(issues)
    else:
        # If no paths are provided, search for .vy files in the current directory recursively
        vy_files = find_vy_files(".")

        if not vy_files:
            print("No .vy files found in the current directory.")
            sys.exit(1)

        issues = [lint_file(file, disabled_rules) for file in vy_files]
        issues_found = any(issues)

    if issues_found:
        sys.exit(1)
    else:
        print("Vyper files are lint free! 🐍")
        sys.exit(0)


if __name__ == "__main__":
    main()
