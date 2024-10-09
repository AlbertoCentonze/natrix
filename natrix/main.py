import os
import glob
import click

from natrix.utils import parse_file_to_ast
from rules import rules

def lint_file(file_path):
    ast = parse_file_to_ast(file_path)

    for rule in rules:
        rule.rule_fn(ast)


def find_vy_files(directory):
    # Recursively find all .vy files in the given directory
    return glob.glob(os.path.join(directory, '**', '*.vy'), recursive=True)

@click.command()
@click.argument('path', required=False, default=None)
def main(path):
    if path:
        if os.path.isfile(path) and path.endswith('.vy'):
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
        vy_files = find_vy_files('.')

        if not vy_files:
            print("No .vy files found in the current directory.")

        for file in vy_files:
            lint_file(file)

if __name__ == '__main__':
    main()