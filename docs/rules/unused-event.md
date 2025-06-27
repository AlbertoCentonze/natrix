# Unused Event

| Property | Value |
|----------|-------|
| Rule Code | `NTX13` |
| Severity | Warning |

## Background
Events are an essential part of smart contract development for monitoring on-chain activity. Defining events that are never emitted represents dead code and may indicate missing functionality.

## Purpose
This rule detects events that are defined in the contract but never emitted via `log` statements.

## Example
```vyper
# Non-compliant code
event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    amount: uint256

event Approval:  # This event is never used
    owner: indexed(address)
    spender: indexed(address)
    amount: uint256

@external
def transfer(to: address, amount: uint256):
    # Only Transfer event is emitted
    log Transfer(msg.sender, to, amount)

# Compliant code
event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    amount: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    amount: uint256

@external
def transfer(to: address, amount: uint256):
    log Transfer(msg.sender, to, amount)

@external
def approve(spender: address, amount: uint256):
    log Approval(msg.sender, spender, amount)  # Now Approval is used
```
