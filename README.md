# Natrix

Natrix is a vyper linter that checks for common mistakes in vyper contracts. It is designed to be your vyper copilot, helping you to write code that is more secure and efficient.

## Installation

You can install Natrix using pip:

```bash
pip install natrix
```

Currently natrix requires [`uv`](https://docs.astral.sh/uv/) to be installed to function correctly.

## Usage

To check a contract:

```bash
natrix file_to_lint.vy
```

To check all vyper contract in the current directory:

```bash
natrix
```

### Command Line Options

```bash
natrix --help                         # Show help message
natrix --version                      # Show version information
natrix --list-rules                   # List all available rules
natrix --disable NTX001 NTX002        # Disable specific rules
natrix --rule-config RuleName.param=value  # Configure rule parameters
```

## Configuration

You can configure Natrix using a `pyproject.toml` file in your project root:

```toml
[tool.natrix]
# Files or directories to lint (relative to pyproject.toml)
files = ["contracts/", "tests/contracts/"]

# Rules to disable
disabled_rules = ["NTX001", "NTX002"]

# Rule-specific configurations
[tool.natrix.rule_configs.RuleName]
param = "value"
```

## Pre-commit hook

Natrix can also be used as a [pre-commit hook](https://pre-commit.com/). This allows to have your contracts checked automatically before you can commit.

To add natrix just add the following lines to your `pre-commit-config.yaml` config file:
```yaml
repos:
  - repo: https://github.com/albertocentonze/natrix
    rev: v0.1.4  # Use the latest version
    hooks:
      - id: natrix
```

and then install pre-commit in your repository by doing:
```bash
pre-commit install
```

## Disclaimer

Natrix is highly experimental software, I do not take any responsibility for changes to the codebase suggested by this linter that might lead to loss of funds or any other issue.
