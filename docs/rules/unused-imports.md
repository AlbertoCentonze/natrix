# Unused Imports

| Property | Value |
|----------|-------|
| Rule Code | `NTX14` |
| Severity | Warning |

## Background
Unused imports make the code harder to understand and maintain. They can mislead developers about the contract's dependencies and may indicate incomplete refactoring or copy-paste errors.

## Purpose
This rule detects import statements that are never referenced in the contract code.

## Example
```vyper
# Non-compliant code
from ethereum.ercs import IERC20  # Warning: Import 'IERC20' is not used
from ethereum.ercs import IERC721  # Warning: Import 'IERC721' is not used

counter: uint256

@external
def increment():
    self.counter += 1

# Compliant code
from ethereum.ercs import IERC20

token: IERC20

@external
def set_token(addr: address):
    self.token = IERC20(addr)
```
