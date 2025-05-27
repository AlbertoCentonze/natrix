# Print Left

| Property | Value |
|----------|-------|
| Rule Code | `NTX6` |
| Severity | Warning |

## Background

`print` statements are typically used for debugging and should be removed from production code. They can increase gas costs and don't serve any functional purpose in a deployed contract.

## Purpose

Detects when `print` statements are left in the code.

## Example

```vyper
@external
def debug_function():
    # Non-compliant - print statement left in the code
    print("Debug info")

@external
def production_function():
    # This function is compliant as it doesn't contain print statements
    pass
```

The `debug_function` would be flagged by this rule because it contains a `print` statement.
