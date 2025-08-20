interface IERC20:
    def transfer(_to: address, _amount: uint256) -> bool: nonpayable
    def totalSupply() -> uint256: view


# This has no memory access but uses an extcall, so it is not a view and should not raise
@external
def transfer(_token: address, _target: address, _amount: uint256):
    assert extcall IERC20(_token).transfer(
        _target, _amount, default_return_value=True
    )


# This is just a staticcall to a view function and should raise
@external
def get_supply(_token: address) -> uint256:
    return staticcall IERC20(_token).totalSupply()
