# pragma version >=0.4.0

# This event is used in the contract
event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    amount: uint256

# This event is never used and should be flagged
event Approval:
    owner: indexed(address)
    spender: indexed(address)
    amount: uint256

# Another unused event
event Mint:
    recipient: indexed(address)
    amount: uint256

# Simple events without parameters
event Paused: pass
event Unpaused: pass

# State variable
balances: HashMap[address, uint256]

@external
def transfer(to: address, amount: uint256) -> bool:
    """Transfer tokens and emit Transfer event."""
    self.balances[msg.sender] -= amount
    self.balances[to] += amount

    # This emits the Transfer event
    log Transfer(msg.sender, to, amount)

    return True

@external
def pause():
    """Pause the contract and emit Paused event."""
    # This emits the Paused event
    log Paused()

@internal
def _mint(to: address, amount: uint256):
    """Internal mint function that forgot to emit the Mint event."""
    self.balances[to] += amount
    # Forgot to emit: log Mint(to, amount)
