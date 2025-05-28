# Implicit Internal

| Property | Value |
|----------|-------|
| Rule Code | `NTX3` |
| Severity | Style |

## Background

Since Vyper 0.4.0 functions without a visibility modifier will be marked as `internal`. Explicitly marking functions as `@internal` improves code clarity.

## Purpose

Detects when internal functions are missing the `@internal` decorator.

## Example

```vyper
# Non-compliant - function is internal but not marked with @internal
def helper_function(x: uint256) -> uint256:
    return x * 2

# Compliant
@internal
def _helper_function(x: uint256) -> uint256:
    return x * 2
```

The `helper_function` would be flagged by this rule because it's not explicitly marked as `@internal`. The `_helper_function` is compliant.
