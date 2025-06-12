# Modifiers Ordering

| Property | Value |
|----------|-------|
| Rule Code | `NTX12` |
| Severity | Style |

## Background

Vyper allows multiple decorators on functions to specify visibility (@external, @internal, @deploy), mutability (@pure, @view, @nonpayable, @payable), and security properties (@nonreentrant). While the compiler accepts these decorators in any order, maintaining a consistent ordering improves code readability and makes the function's properties immediately clear to readers.

## Purpose

Enforces a consistent ordering of function modifiers in Vyper contracts. The recommended order is:

1. **Visibility** decorators first (@external, @internal, @deploy)
2. **Mutability** decorators second (@pure, @view, @nonpayable, @payable)
3. **Security** decorators last (@nonreentrant)

## Example

```vyper
# Non-compliant - incorrect ordering
@view
@external  # visibility should come before mutability
def get_balance() -> uint256:
    return self.balance

@nonreentrant
@external  # visibility should come before security
@payable
def deposit():
    self.balance += msg.value

# Compliant - correct ordering
@external  # visibility first
@view      # mutability second
def get_balance_correct() -> uint256:
    return self.balance

@external     # visibility first
@payable      # mutability second
@nonreentrant # security last
def deposit_correct():
    self.balance += msg.value

# Functions without explicit visibility (defaults to internal)
# Non-compliant
@nonreentrant
@view  # mutability should come before security
def internal_func() -> uint256:
    return self.balance

# Compliant
@view         # mutability first
@nonreentrant # security second
def internal_func_correct() -> uint256:
    return self.balance
```
