from __future__ import annotations

import sys
import os
import argparse
import re
from typing import Set, List, Dict, Any, Optional
import json
from dataclasses import asdict

# Import tomllib for Python 3.11+ or tomli for earlier versions
try:
    import tomllib
except ImportError:
    import tomli as tomllib

from natrix.__version__ import __version__
from natrix.ast_tools import parse_file
from natrix.rules.common import RuleRegistry, Issue


class OutputFormatter:
    """Handles output formatting for both CLI and JSON modes."""

    def __init__(self, json_mode: bool = False):
        self.json_mode = json_mode
        self.messages: List[str] = []  # Collect non-issue messages for JSON mode

    def print(self, message: str) -> None:
        """Print a message (only in CLI mode)."""
        if not self.json_mode:
            print(message)
        else:
            # In JSON mode, we might want to collect these for debugging
            self.messages.append(message)

    def print_issues(self, issues: List[Issue]) -> None:
        """Print all issues in the appropriate format."""
        if self.json_mode:
            # Convert Issue objects to dictionaries, excluding source_code for JSON output
            json_issues = []
            for issue in issues:
                issue_dict = asdict(issue)
                # Remove source_code from JSON output as it's for CLI display only
                issue_dict.pop("source_code", None)
                json_issues.append(issue_dict)
            print(json.dumps(json_issues, indent=2))
        else:
            # Print issues with spacing between them
            for i, issue in enumerate(issues):
                if i > 0:  # Add a blank line between issues
                    print()
                print(issue.cli_format())

    def print_summary(self, has_issues: bool) -> None:
        """Print the final summary message."""
        if self.json_mode:
            return

        if has_issues:
            print("\nFound issues in files.")
        else:
            print("Vyper files are lint free! 🐍")


def lint_file(
    file_path: str,
    formatter: OutputFormatter,
    disabled_rules: Optional[Set[str]] = None,
    extra_paths: List[str] = [],
) -> List[Issue]:
    """Lint a single Vyper file with the given rules configuration."""
    ast = parse_file(file_path, extra_paths=extra_paths)

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
            formatter.print(
                f"Error running rule {rule.run}: {str(e)}. Please report this issue on GitHub."
            )

    return issues


def find_vy_files(directory: str) -> List[str]:
    # Recursively find all .vy files in the given directory, excluding specified directories
    vy_files = []
    for root, dirs, files in os.walk(directory):
        # Collect all .vy files
        for file in files:
            if file.endswith(".vy"):
                vy_files.append(os.path.join(root, file))

    return vy_files


def get_project_root() -> str:
    """Get the project root directory, which contains the pyproject.toml file."""
    # First try to find it from the current working directory upwards
    current_dir = os.path.abspath(os.getcwd())

    while current_dir != os.path.dirname(current_dir):  # Stop at root
        if os.path.exists(os.path.join(current_dir, "pyproject.toml")):
            return current_dir
        current_dir = os.path.dirname(current_dir)

    # If not found, default to the current directory
    return os.getcwd()


def read_pyproject_config() -> Dict[str, Any]:
    """Read configurations from pyproject.toml if it exists"""
    config: Dict[str, Any] = {
        "files": [],
        "disabled_rules": set(),
        "rule_configs": {},
        "path": [],
    }

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
                    # Parse path configurations
                    if "path" in natrix_config and isinstance(
                        natrix_config["path"], list
                    ):
                        # Make paths relative to pyproject.toml location
                        config["path"] = [
                            os.path.normpath(os.path.join(project_root, path))
                            for path in natrix_config["path"]
                        ]
    except Exception as e:
        print(f"Warning: Error reading pyproject.toml: {e}")

    return config


def parse_args() -> argparse.Namespace:
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
        help="List of rule codes to disable (e.g., --disable NTX3 NTX7).",
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
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        nargs="+",
        help="List of additional paths to search for imports (e.g., -p /path/to/libs /another/path).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output issues in JSON format.",
    )
    return parser.parse_args()


def main() -> None:
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

    # Create the output formatter
    formatter = OutputFormatter(json_mode=args.json)

    # Parse rule configurations from CLI
    rule_configs: Dict[str, Dict[str, Any]] = {}
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
                formatter.print(f"Invalid rule configuration format: {config_str}")
                formatter.print("Expected format: RuleName.param=value")
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

    # Combine paths from CLI and pyproject.toml
    extra_paths = pyproject_config.get("path", [])
    if args.path:
        extra_paths.extend(args.path)

    # Handle files
    if args.files:
        all_vy_files = []
        for path in args.files:
            if os.path.isfile(path) and path.endswith(".vy"):
                all_vy_files.append(path)
            elif os.path.isdir(path):
                dir_vy_files = find_vy_files(path)
                if not dir_vy_files:
                    formatter.print(f"No .vy files found in the directory: {path}")
                all_vy_files.extend(dir_vy_files)
            else:
                formatter.print(
                    f"Provided path is not a valid .vy file or directory: {path}"
                )

        if not all_vy_files:
            formatter.print("No valid .vy files to lint.")
            sys.exit(1)
    else:
        # If no paths are provided, search for .vy files in the current directory recursively
        all_vy_files = find_vy_files(".")

        if not all_vy_files:
            formatter.print("No .vy files found in the current directory.")
            sys.exit(1)

    # Collect all issues from all files
    all_issues: List[Issue] = []
    for file in all_vy_files:
        file_issues = lint_file(
            file, formatter, disabled_rules, extra_paths=extra_paths
        )
        all_issues.extend(file_issues)

    # Output issues
    formatter.print_issues(all_issues)

    # Print summary and exit
    formatter.print_summary(bool(all_issues))
    sys.exit(1 if all_issues else 0)


if __name__ == "__main__":
    main()
