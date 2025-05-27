# Argument Naming Convention

| Property | Value |
|----------|-------|
| Rule Code | `NTX11` |
| Severity | Warning |
| Configuration | `pattern` - Regex pattern for argument naming convention (default: `^_`) |

## Background

Consistent naming conventions improve code readability and maintainability. Prefixing arguments (e.g., with `_`) can help distinguish them from local variables or state variables at a glance.

## Purpose

Ensures that function arguments follow a specified naming convention. By default, arguments should start with an underscore (`_`).



## Example

Consider the following Vyper code:

```vyper
# Non-compliant - argument 'arg1' does not start with '_'
@external
def myFunction(arg1: uint256, _arg2: String[10]):
    pass

# Compliant
@external
def anotherFunction(_input_value: address, _another_param: bool):
    pass
```

In the `myFunction` example, `arg1` would be flagged by this rule because it does not start with an underscore. `_arg2` is compliant. In `anotherFunction`, both arguments `_input_value` and `_another_param` are compliant.

## Configuration

This rule can be customized by adjusting the naming pattern:

- `pattern` (string): Regular expression pattern that argument names must match (default: `^_`)

### pyproject.toml

```toml
[tool.natrix.rule_configs.ArgumentNaming]
pattern = "^_"  # Default: Arguments must start with underscore
```

### Command Line Configuration
```bash
# Use snake_case for arguments
natrix --rule-config ArgumentNaming.pattern="^[a-z_][a-z0-9_]*$"
```

### Class Instantiation
```python
# Require camelCase for arguments
ArgumentNamingRule(pattern="^[a-z][a-zA-Z0-9]*$")
```
