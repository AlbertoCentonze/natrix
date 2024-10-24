import glob
import os

import click

from natrix.rules import rules
from natrix.rules.common import Issue
from natrix.ast_tools import parse_file


def cli_format_issues(issue: Issue):
    return (
        f"{issue.file}:{issue.position} {issue.severity} {issue.code}: {issue.message}"
    )


def lint_file(file_path):
    ast = parse_file(file_path)

    # flatmaps the issues from all rules
    issues = [issue for rule in rules for issue in rule.run(ast)]

    for issue in issues:
        print(cli_format_issues(issue))


def find_vy_files(directory):
    # Recursively find all .vy files in the given directory
    return glob.glob(os.path.join(directory, "**", "*.vy"), recursive=True)


@click.command()
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
    else:
        # If no path is provided, search for .vy files in the current directory recursively
        vy_files = find_vy_files(".")

        if not vy_files:
            print("No .vy files found in the current directory.")

        for file in vy_files:
            lint_file(file)


if __name__ == "__main__":
    main()
