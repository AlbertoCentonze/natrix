import sys

import click

from natrix.__version__ import __version__


import glob
import os

from natrix.rules import rules
from natrix.ast_tools import parse_file


def lint_file(file_path):
    ast = parse_file(file_path)

    # flatmaps the issues from all rules
    issues = [issue for rule in rules for issue in rule.run(ast)]

    for issue in issues:
        print(issue.cli_format())

    if issues:
        sys.exit(1)


def find_vy_files(directory):
    # Recursively find all .vy files in the given directory
    return glob.glob(os.path.join(directory, "**", "*.vy"), recursive=True)


@click.command()
@click.version_option(__version__)
@click.argument(
    "path",
    required=False,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True),
)
def main(path):
    if path:
        if os.path.isfile(path) and path.endswith(".vy"):
            # If a specific .vy file is provided
            lint_file(path)
        elif os.path.isdir(path):
            # If a directory is provided, find all .vy files in it
            vy_files = find_vy_files(path)
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

        for file in vy_files:
            lint_file(file)

    print("Vyper files are lint free! 🐍")
    sys.exit(0)
