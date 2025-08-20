from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

# Import tomllib for Python 3.11+ or tomli for earlier versions
try:
    import tomllib
except ImportError:
    import tomli as tomllib

from natrix.__version__ import __version__
from natrix.codegen import generate_call_graph, generate_exports
from natrix.context import ProjectContext
from natrix.rules.common import Issue, RuleRegistry

# Vyper file extensions
VYPER_EXTENSIONS = (".vy", ".vyi")


class OutputFormatter:
    """Handles output formatting for both CLI and JSON modes."""

    def __init__(self, json_mode: bool = False):
        self.json_mode = json_mode
        self.messages: list[str] = []  # Collect non-issue messages for JSON mode

    def print(self, message: str) -> None:
        """Print a message (only in CLI mode)."""
        if not self.json_mode:
            print(message)
        else:
            # In JSON mode, we might want to collect these for debugging
            self.messages.append(message)

    def print_issues(self, issues: list[Issue]) -> None:
        """Print all issues in the appropriate format."""
        if self.json_mode:
            # Convert Issue objects to dictionaries,
            # excluding source_code for JSON output
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
    file_path: Path,
    project_context: ProjectContext,
    formatter: OutputFormatter,
    disabled_rules: set[str] | None = None,
) -> list[Issue]:
    """Lint a single Vyper file using the pre-built project context."""
    if disabled_rules is None:
        disabled_rules = set()

    # Get the rule instances (already instantiated once at startup)
    rules = RuleRegistry.get_rules()

    # Flatten the issues from all rules and filter out disabled rules
    issues = []
    for rule in rules:
        try:
            rule_issues = rule.run(project_context, file_path)
            issues.extend(
                [issue for issue in rule_issues if issue.code not in disabled_rules]
            )
        except Exception as e:
            # Simple error message with suggestion to report the issue
            formatter.print(
                f"Error running rule {rule.run}: {e!s}. "
                "Please report this issue on GitHub."
            )

    return issues


def find_vy_files(directory: Path, exclude_paths: list[Path] | None = None) -> list[Path]:
    # Recursively find all Vyper files (.vy and .vyi) in the given directory,
    # excluding specified files and directories
    if exclude_paths is None:
        exclude_paths = []
    
    vy_files = []
    for root, _, files in os.walk(directory):
        # Collect all Vyper files
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in VYPER_EXTENSIONS:
                # Check if this file should be excluded
                file_path_resolved = file_path.resolve()
                should_exclude = False
                
                for exclude_path in exclude_paths:
                    exclude_path_resolved = exclude_path.resolve()
                    # Check if file matches exactly or is within an excluded directory
                    if (file_path_resolved == exclude_path_resolved or 
                        exclude_path_resolved in file_path_resolved.parents):
                        should_exclude = True
                        break
                
                if not should_exclude:
                    vy_files.append(file_path)

    return vy_files


def get_project_root() -> Path:
    """Get the project root directory, which contains the pyproject.toml file."""
    # First try to find it from the current working directory upwards
    current_path = Path.cwd().resolve()

    for parent in [current_path, *current_path.parents]:
        if (parent / "pyproject.toml").exists():
            return parent

    # If not found, default to the current directory
    return Path.cwd()


def read_pyproject_config() -> dict[str, Any]:
    """Read configurations from pyproject.toml if it exists"""
    config: dict[str, Any] = {
        "files": [],
        "disabled_rules": set(),
        "rule_configs": {},
        "path": [],
        "exclude": [],
    }

    try:
        # Find the project root directory
        project_root = get_project_root()
        pyproject_path = project_root / "pyproject.toml"

        if pyproject_path.exists():
            with pyproject_path.open("rb") as f:
                pyproject = tomllib.load(f)
                if "tool" in pyproject and "natrix" in pyproject["tool"]:
                    natrix_config = pyproject["tool"]["natrix"]
                    if "files" in natrix_config and isinstance(
                        natrix_config["files"], list
                    ):
                        # Make paths relative to pyproject.toml location
                        config["files"] = [
                            (project_root / path).resolve()
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
                            (project_root / path).resolve()
                            for path in natrix_config["path"]
                        ]
                    if "exclude" in natrix_config and isinstance(
                        natrix_config["exclude"], list
                    ):
                        config["exclude"] = [
                            (project_root / path).resolve()
                            for path in natrix_config["exclude"]
                        ]
    except Exception as e:
        print(f"Warning: Error reading pyproject.toml: {e}")

    return config


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="A linter for Vyper Smart Contracts.")

    # Add version flag at the top level
    parser.add_argument(
        "-v", "--version", action="store_true", help="Show version and exit."
    )

    # Create subparsers
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create the lint subcommand parser
    lint_parser = subparsers.add_parser("lint", help="Lint Vyper files")
    lint_parser.add_argument(
        "files",
        nargs="*",
        help=(
            "Path(s) to vyper file(s) or directory/directories to lint. "
            "If not provided, all vyper files in current directory are checked."
        ),
    )
    lint_parser.add_argument(
        "-d",
        "--disable",
        type=str,
        nargs="+",
        help="List of rule codes to disable (e.g., --disable NTX3 NTX7).",
    )
    lint_parser.add_argument(
        "-c",
        "--rule-config",
        action="append",
        help=(
            "Configure rules with format 'RuleName.param=value'. "
            "Can be used multiple times. Example: ArgNamingConvention.pattern=^_"
        ),
    )
    lint_parser.add_argument(
        "-l",
        "--list-rules",
        action="store_true",
        help="List all available rules with their descriptions.",
    )
    lint_parser.add_argument(
        "-p",
        "--path",
        type=str,
        nargs="+",
        help=(
            "List of additional paths to search for imports "
            "(e.g., -p /path/to/libs /another/path)."
        ),
    )
    lint_parser.add_argument(
        "--json",
        action="store_true",
        help="Output issues in JSON format.",
    )
    lint_parser.add_argument(
        "-e",
        "--exclude",
        type=str,
        nargs="+",
        help="List of files or directories to exclude from linting (e.g., --exclude tests/ build/).",
    )

    # Create the codegen subcommand parser
    codegen_parser = subparsers.add_parser("codegen", help="Code generation utilities")
    codegen_subparsers = codegen_parser.add_subparsers(
        dest="codegen_command", help="Code generation commands"
    )

    # Create the exports sub-subcommand
    exports_parser = codegen_subparsers.add_parser(
        "exports", help="Generate explicit exports for a contract"
    )
    exports_parser.add_argument("file_path", help="Path to the Vyper contract file")
    exports_parser.add_argument(
        "-p",
        "--path",
        type=str,
        nargs="+",
        help=(
            "List of additional paths to search for imports "
            "(e.g., -p /path/to/libs /another/path)."
        ),
    )

    # Create the call_graph sub-subcommand
    call_graph_parser = codegen_subparsers.add_parser(
        "call_graph", help="Generate a Mermaid call graph for a contract"
    )
    call_graph_parser.add_argument(
        "file_path",
        help="Path to the Vyper contract file, optionally with :function_name suffix",
    )
    call_graph_parser.add_argument(
        "-p",
        "--path",
        type=str,
        nargs="+",
        help=(
            "List of additional paths to search for imports "
            "(e.g., -p /path/to/libs /another/path)."
        ),
    )

    # If no command is specified, default to lint for backward compatibility
    args = parser.parse_args()
    if args.command is None and not args.version:
        # Re-parse with lint as default command
        sys.argv.insert(1, "lint")
        args = parser.parse_args()

    return args


def main() -> None:
    """Main entry point for the linter."""
    args = parse_args()

    if args.version:
        print(f"natrix v{__version__}")
        sys.exit(0)

    # Handle codegen command
    if args.command == "codegen":
        if args.codegen_command == "exports":
            # Get extra paths if provided
            extra_paths = tuple(Path(p) for p in args.path) if args.path else ()
            # Generate and print exports
            exports = generate_exports(Path(args.file_path), extra_paths)
            print(exports)
            sys.exit(0)
        elif args.codegen_command == "call_graph":
            # Parse file path and optional function name
            file_path_str = args.file_path
            target_function = None

            # Check if function name is specified with :function_name syntax
            if ":" in file_path_str:
                file_path_str, target_function = file_path_str.rsplit(":", 1)

            # Get extra paths if provided
            extra_paths = tuple(Path(p) for p in args.path) if args.path else ()

            # Generate and print call graph
            call_graph = generate_call_graph(
                Path(file_path_str), extra_paths, target_function
            )
            print(call_graph)
            sys.exit(0)
        else:
            print("Error: No codegen subcommand specified")
            sys.exit(1)

    # Handle lint command (default behavior)
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
    rule_configs: dict[str, dict[str, Any]] = {}
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

    # Combine exclude paths from CLI and pyproject.toml
    exclude_paths = pyproject_config.get("exclude", [])
    if args.exclude:
        exclude_paths.extend([Path(p).resolve() for p in args.exclude])

    # Handle files
    if args.files:
        all_vy_files = []
        for path in args.files:
            path = Path(path)
            if path.is_file() and path.suffix in VYPER_EXTENSIONS:
                all_vy_files.append(path)
            elif path.is_dir():
                dir_vy_files = find_vy_files(path, exclude_paths)
                if not dir_vy_files:
                    formatter.print(f"No Vyper files found in the directory: {path}")
                all_vy_files.extend(dir_vy_files)
            else:
                formatter.print(
                    f"Provided path is not a valid Vyper file or directory: {path}"
                )

        if not all_vy_files:
            formatter.print("No valid Vyper files to lint.")
            sys.exit(1)
    else:
        # If no paths are provided, search for Vyper files in the current
        # directory recursively
        all_vy_files = find_vy_files(Path(), exclude_paths)

        if not all_vy_files:
            formatter.print("No Vyper files found in the current directory.")
            sys.exit(1)

    # Create ProjectContext with all files
    formatter.print("Building project dependency graph...")
    project_context = ProjectContext(
        all_vy_files,
        extra_paths=tuple(Path(p) if isinstance(p, str) else p for p in extra_paths),
    )

    # Collect all issues from all files
    all_issues: list[Issue] = []
    for file in all_vy_files:
        file_issues = lint_file(
            Path(file).resolve(), project_context, formatter, disabled_rules
        )
        all_issues.extend(file_issues)

    # Output issues
    formatter.print_issues(all_issues)

    # Print summary and exit
    formatter.print_summary(bool(all_issues))
    sys.exit(1 if all_issues else 0)


if __name__ == "__main__":
    main()
