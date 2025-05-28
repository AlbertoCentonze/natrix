# Cache Storage Variable

| Property | Value |
|----------|-------|
| Rule Code | `NTX7` |
| Severity | Optimization |

!!! warning "Experimental Rule"
    This rule is currently experimental and not enabled by default. It is available in the codebase for testing purposes but is not yet production-ready.

## Background

Reading from storage is one of the most gas-expensive operations in Vyper (and Ethereum in general). Caching storage variables in memory when they are accessed multiple times can significantly reduce gas costs.

## Purpose

Detects when a storage variable is accessed multiple times in a function and suggests caching it to save gas.

## Example

```vyper
# Storage variable
user_balance: public(uint256)

# Non-compliant - accessing storage variable multiple times
@external
def process_balance() -> uint256:
    if self.user_balance > 100:
        return self.user_balance - 100
    else:
        return self.user_balance

# Compliant - caching storage variable
@external
def process_balance_cached() -> uint256:
    balance_cache: uint256 = self.user_balance
    if balance_cache > 100:
        return balance_cache - 100
    else:
        return balance_cache
```

The `process_balance` function would be flagged by this rule because it accesses `self.user_balance` multiple times. The `process_balance_cached` function is compliant because it caches the storage variable.
