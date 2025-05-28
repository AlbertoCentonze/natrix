# Constant Naming Convention

| Property | Value |
|----------|-------|
| Rule Code | `NTX2` |
| Severity | Style |

## Background

Using `UPPER_SNAKE_CASE` for constants is a widely adopted convention that improves code readability by making it easy to distinguish constants from other variables.

## Purpose

Ensures that constants are named in `UPPER_SNAKE_CASE`.

## Example

Consider the following Vyper code:

```vyper
# Non-compliant - constant 'threshold_value' is not in UPPER_SNAKE_CASE
threshold_value: constant(uint256) = 1000

# Compliant
MAX_VALUE: constant(uint256) = 1000
TOTAL_SUPPLY: constant(uint256) = 100000
```

In this example, `threshold_value` would be flagged by the rule. `MAX_VALUE` and `TOTAL_SUPPLY` are compliant.
