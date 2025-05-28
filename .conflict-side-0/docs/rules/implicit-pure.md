# Implicit Pure

| Property | Value |
|----------|-------|
| Rule Code | `NTX5` |
| Severity | Style |

## Background

Similar to [the implicit view rule](implicit-view.md). Using the `@pure` decorator for functions that don't access state is not enforced by the compiler, but helps querying the function off-chain and helps preventing the introduction of side effects in the function.

## Purpose

Detects when functions that don't access state at all are missing the `@pure` decorator.

## Example

```vyper
# Non-compliant - function doesn't access state but isn't marked as @pure
@external
def calculate_sum(_a: uint256, _b: uint256) -> uint256:
    return _a + _b

# Compliant
@pure
@external
def calculate_sum_pure(_a: uint256, _b: uint256) -> uint256:
    return _a + _b
```

The first `calculate_sum` function would be flagged by this rule because it doesn't access state at all but is not marked as `@pure`.
