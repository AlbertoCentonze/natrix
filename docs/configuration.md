# Configuration

Natrix can be configured using a `pyproject.toml` file in your project root. All configuration options are placed under the `[tool.natrix]` section.

## Basic Configuration

```toml
[tool.natrix]
# Files or directories to lint (relative to pyproject.toml location)
files = ["contracts/", "tests/contracts/"]

# Rules to disable globally
disabled_rules = ["NTX1", "NTX2"]

# Rule-specific configurations
[tool.natrix.rule_configs.MemoryExpansion]
max_frame_size = 25000

[tool.natrix.rule_configs.ArgNamingConvention]
pattern = "^_[a-z][a-z0-9_]*$"
```

## Configuration Options

### Files to Lint

Specify which files or directories natrix should analyze:

```toml
[tool.natrix]
# Single file
files = ["contract.vy"]

# Multiple files and directories
files = ["contracts/", "tests/", "standalone.vy"]

# Relative paths are resolved relative to pyproject.toml location
files = ["src/contracts/", "../shared/contracts/"]
```

If no `files` configuration is provided, natrix will scan the current directory and all subdirectories for `.vy` files.

### Disabling Rules

Disable specific rules globally across your project:

```toml
[tool.natrix]
# Disable single rule
disabled_rules = ["NTX8"]

# Disable multiple rules
disabled_rules = ["NTX1", "NTX7", "NTX11"]
```

You can find all available rule codes by running:
```bash
natrix --list-rules
```

### Rule-Specific Configuration

Some rules accept configuration parameters to customize their behavior. Only two rules currently have configurable parameters:

**Memory Expansion Rule (NTX1)**
```toml
[tool.natrix.rule_configs.MemoryExpansion]
max_frame_size = 25000  # Default: 20000
```

**Argument Naming Convention Rule (NTX11)**
```toml
[tool.natrix.rule_configs.ArgNamingConvention]
pattern = "^_[a-z][a-z0-9_]*$"  # Default: "^_"
```

For detailed configuration examples and advanced usage, see the individual rule documentation pages in the [Rules](./rules/index.md) section.

## Example Configurations

=== "DeFi Protocol"
    ```toml
    [tool.natrix]
    files = ["contracts/core/", "contracts/interfaces/", "tests/unit/"]
    disabled_rules = ["NTX7"]

    [tool.natrix.rule_configs.MemoryExpansion]
    max_frame_size = 15000

    [tool.natrix.rule_configs.ArgNamingConvention]
    pattern = "^_[a-z][a-z0-9_]*$"
    ```

=== "Learning Project"
    ```toml
    [tool.natrix]
    files = ["contracts/", "examples/"]
    disabled_rules = ["NTX7"]

    [tool.natrix.rule_configs.MemoryExpansion]
    max_frame_size = 35000
    ```

=== "Minimal"
    ```toml
    [tool.natrix]
    disabled_rules = ["NTX7"]
    ```
