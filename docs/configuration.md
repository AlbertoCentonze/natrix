# Configuration

Natrix can be configured using a `pyproject.toml` file in your project root. All configuration options are placed under the `[tool.natrix]` section.

## Basic Configuration

```toml
[tool.natrix]
# Files or directories to lint (relative to pyproject.toml location)
files = ["contracts/", "tests/contracts/"]

# Rules to disable globally
disabled_rules = ["NTX1", "NTX2"]

# Additional paths to search for imports
path = ["lib", "vendor/contracts"]

# Files or directories to exclude from linting
exclude = ["build/", "tests/mocks/"]

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

### Import Paths

Specify additional paths where the Vyper compiler should look for imports:

```toml
[tool.natrix]
# Single path
path = ["lib"]

# Multiple paths
path = ["lib", "vendor/contracts", "../shared"]

# Paths are resolved relative to pyproject.toml location
```

By default, natrix includes:
1. All Python system paths (same paths Python uses for imports, obtained via `sys.path`)
2. `lib/pypi` - the default dependency folder for moccasin

Additional paths specified here will be added to these defaults.

This is equivalent to using the `-p` flag in the command line:
```bash
natrix contract.vy -p lib vendor/contracts ../shared
```

### Excluding Files and Directories

Exclude specific files or directories from linting:

```toml
[tool.natrix]
# Exclude single directory
exclude = ["build/"]

# Exclude multiple files and directories
exclude = ["build/", "tests/mocks/", "temp.vy"]

# Relative paths are resolved relative to pyproject.toml location
exclude = ["contracts/legacy/", "../generated/contracts/"]
```

Files and directories in the exclude list will be completely ignored during linting. This is useful for:
- Third-party modules
- Mock contracts from other projects
- Deployed legacy code that should remain unchanged

You can also exclude files via command line:
```bash
natrix --exclude build/ tests/fixtures/ temp.vy
```

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

## JSON Output Mode

Natrix supports JSON output for programmatic integration with IDEs, CI/CD pipelines, and other development tools.

Enable JSON output with the `--json` flag:

```bash
natrix contract.vy --json
```

This outputs issues as a JSON array instead of the default colored terminal output, making it easy to parse and process results programmatically.

## Example Configurations

=== "DeFi Protocol"
    ```toml
    [tool.natrix]
    files = ["contracts/core/", "contracts/interfaces/", "tests/unit/"]
    path = ["lib/snekmate", "lib/vyper-utils"]
    exclude = ["contracts/legacy/", "test/mocks/"]
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
