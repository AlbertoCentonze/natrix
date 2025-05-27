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
