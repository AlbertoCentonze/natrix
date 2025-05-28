# Unused Variable

| Property | Value |
|----------|-------|
| Rule Code | `NTX8` |
| Severity | Warning |

## Background

Unused variables can indicate mistakes in the code (forgotten logic) or unnecessary code that increases complexity and gas costs.

## Purpose

Detects variables that are declared but never used within a function.

## Example

```vyper
@external
def process_data(_value: uint256) -> uint256:
    # Non-compliant - variable declared but never used
    temp: uint256 = _value * 2

    return _value

@external
def process_data_fixed(_value: uint256) -> uint256:
    # Compliant - all declared variables are used
    temp: uint256 = _value * 2

    return temp
```

The `process_data` function would be flagged by this rule because the `temp` variable is declared but never used.

### Intentionally Unused Variables in For Loops

When you need to iterate a specific number of times but don't actually use the loop variable, you can use the underscore (`_`) convention to indicate that the variable is intentionally unused. This prevents the linter from reporting it as an unused variable.

```vyper
@external
def repeat_operation(count: uint256):
    # Non-compliant - 'i' is declared but never used
    for i: uint256 in range(count):
        # Some operation that doesn't use 'i'
        pass

@external
def repeat_operation_fixed(count: uint256):
    # Compliant - using '_' indicates intentionally unused variable
    for _: uint256 in range(count):
        # Some operation that doesn't use the loop variable
        pass
```

By naming the loop variable `_`, you signal to both the linter and other developers that the variable is intentionally unused, preventing false positive warnings.
