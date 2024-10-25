import sys
import click
import os
from natrix.__version__ import __version__
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


def find_vy_files(directory, exclude_dirs):
    # Recursively find all .vy files in the given directory, excluding specified directories
    vy_files = []
    for root, dirs, files in os.walk(directory):
        # Remove excluded directories from the walk
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in exclude_dirs]

        # Collect all .vy files
        for file in files:
            if file.endswith(".vy"):
                vy_files.append(os.path.join(root, file))

    return vy_files


@click.command()
@click.version_option(__version__)
@click.argument(
    "path",
    required=False,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True),
)
@click.option(
    "--exclude",
    multiple=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
    help="Directories to exclude from the linting process.",
)
def main(path, exclude):
    exclude_dirs = [os.path.abspath(ex_dir) for ex_dir in exclude]

    if path:
        if os.path.isfile(path) and path.endswith(".vy"):
            # If a specific .vy file is provided
            lint_file(path)
        elif os.path.isdir(path):
            # If a directory is provided, find all .vy files in it (even if the directory name ends with .vy)
            vy_files = find_vy_files(path, exclude_dirs)
            if not vy_files:
                print(f"No .vy files found in the directory: {path}")
            for file in vy_files:
                lint_file(file)
        else:
            print("Provided path is not a valid .vy file or directory.")
            sys.exit(1)
    else:
        # If no path is provided, search for .vy files in the current directory recursively
        vy_files = find_vy_files(".", exclude_dirs)

        if not vy_files:
            print("No .vy files found in the current directory.")
            sys.exit(1)

        for file in vy_files:
            lint_file(file)

    print("Vyper files are lint free! 🐍")
    sys.exit(0)


if __name__ == "__main__":
    main()
