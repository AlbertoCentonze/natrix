# pragma version ~=0.4.0

from ethereum.ercs import ERC20

SOME_BOUND: constant(uint256) = 40

array_with_magic_bound: DynArray[uint256, 1234]
array_with_constant_bound: DynArray[uint256, SOME_BOUND]

fixed_array_with_magic_bound: uint256[5678]
fixed_array_with_constant_bound: uint256[SOME_BOUND]

some_addy: address

@payable
@external
@view
@nonreentrant
def modifiers():
    pass


@nonreentrant
@view
@external
@payable
def modifiers_shuffled():
    pass

@internal
def internal_without_underscore():
    self.array_with_magic_bound[1001] = 487
    self.array_with_magic_bound[SOME_BOUND] = 124

    if self.fixed_array_with_magic_bound[2] == 0:
        pass

    if self.fixed_array_with_magic_bound[SOME_BOUND] == 0:
        pass

    pass

def _set_some_addy(new_addy: address):
    self.some_addy = new_addy

@external
def set_some_addy(new_addy: address):
    assert new_addy != convert(42, address)

    _set_some_addy(new_addy)

@external
def set_some_addy_alt(new_addy: address):
    if new_addy == empty(address):
        raise "nogo buddy"

    _set_some_addy(new_addy)

@external
def set_some_addy_no_check(new_addy: address):
    _set_some_addy(new_addy)
