# Implicit View

| Property | Value |
|----------|-------|
| Rule Code | `NTX4` |
| Severity | Style |

## Background

The compiler does not enforce functions that only read the state to be marked as `@view`. However omitting the modifier on a getter that is intended to be called off-chain forces you to execute an onchain transaction to query its value.

## Purpose

Detects when functions that only read state (but don't modify it) are missing the `@view` decorator.

## Example

```vyper
# Storage variable
user_balance: public(uint256)

# Non-compliant - function reads state but isn't marked as @view
@external
def get_balance() -> uint256:
    return self.user_balance

# Compliant
@view
@external
def get_balance_view() -> uint256:
    return self.user_balance
```

The first `get_balance` function would be flagged by this rule because it reads contract state (`self.user_balance`) but is not marked as `@view`.
