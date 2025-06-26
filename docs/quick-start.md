# Quick Start

This guide will help you get up and running with Natrix quickly.

## Prerequisites

- Python (version 3.10 or higher)

## Installation

You can install Natrix using various package managers:

=== "pip"

    ```bash
    pip install natrix
    ```

=== "uv"

    ```bash
    uv add natrix
    ```

=== "poetry"
    ```bash
    poetry add natrix
    ```

## Usage

To analyze a Vyper contract:

```bash
natrix lint path/to/your/contract.vy
# or simply
natrix path/to/your/contract.vy
```

You can also analyze multiple files at once:

```bash
natrix lint path/to/contracts/
# or simply
natrix path/to/contracts/
```

### Code Generation

Natrix can also generate code snippets to help fix certain issues. For example, to generate explicit exports for a contract:

```bash
natrix codegen exports path/to/your/contract.vy
```

## Integration with pre-commit

You can use Natrix with [pre-commit](https://pre-commit.com/) to automatically lint your Vyper files before each commit.

1. Add a `.pre-commit-config.yaml` file to your project with the following content:

```yaml
repos:
- repo: https://github.com/AlbertoCentonze/natrix
rev: v0.1.9  # Use the latest version
hooks:
    - id: natrix
```

2. Install the hooks:

```bash
pre-commit install
```

## Next Steps

- For advanced configuration options, see the [Configuration](./configuration.md) guide
- Explore the available [Rules](./rules/index.md) to understand what Natrix can check for
- Learn more about [Development](./development/index.md) if you want to contribute
