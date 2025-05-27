# Unused Argument

| Property | Value |
|----------|-------|
| Rule Code | `NTX10` |
| Severity | Warning |

## Background

Unused arguments can indicate mistakes in the code (forgotten logic) or unnecessary parameters that increase complexity and gas costs.

## Purpose

Detects function arguments that are declared but never used within the function.

## Example

```vyper
# Non-compliant - argument '_unused' is never used in the function
@external
def process(_value: uint256, _unused: address) -> uint256:
    return _value * 2

# Compliant - all arguments are used
@external
def process_fixed(_value: uint256, _modifier: uint256) -> uint256:
    return _value * _modifier
```

The `process` function would be flagged by this rule because the `_unused` argument is declared but never used within the function.
