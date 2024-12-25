import sys
import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

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


class NatrixSettings(BaseSettings):
    """
    A linter for Vyper Smart Contracts.
    """

    # ^ What is written above appears in the cli help message
    model_config = SettingsConfigDict(
        env_file=".env",
        toml_file="natrix.toml",
        pyproject_toml_table_header=("tool", "natrix"),
        cli_parse_args=True,
        cli_implicit_flags=True,
        cli_enforce_required=False,
    )

    include: Optional[str] = Field(
        None,
        description="Path to a vyper file or directory. If not provided, all vyper files in current directory are checked.",
    )
    version: bool = Field(False, description="Show version and exit.")


def main():
    issues_found = False

    settings = NatrixSettings()

    if settings.version:
        print(__version__)
        sys.exit(0)

    if settings.include:
        print(settings.include)
        if os.path.isfile(settings.include) and settings.include.endswith(".vy"):
            # If a specific .vy file is provided
            lint_file(settings.include)
        elif os.path.isdir(settings.include):
            # If a directory is provided, find all .vy files in it
            vy_files = find_vy_files(settings.include)
            if not vy_files:
                print(f"No .vy files found in the directory: {settings.include}")
            for file in vy_files:
                lint_file(file)
        else:
            print("Provided path is not a valid .vy file or directory.")
            sys.exit(1)
    else:
        # If no path is provided, search for .vy files in the current directory recursively
        vy_files = find_vy_files(".")

        if not vy_files:
            print("No .vy files found in the current directory.")
            sys.exit(1)

        issues = [lint_file(file) for file in vy_files]
        issues_found = any(issues)
        sys.exit()

    if not issues_found:
        print("Vyper files are lint free! 🐍")
        sys.exit(0)


if __name__ == "__main__":
    main()
