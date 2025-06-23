# @version >=0.4.1

# Correct ordering examples

@external
@view
def correct_external_view() -> uint256:
    return 42

@internal
@pure
def correct_internal_pure() -> uint256:
    return 123

@external
@payable
def correct_external_payable():
    pass

@external
@nonreentrant
def correct_external_nonreentrant():
    pass

@external
@view
@nonreentrant
def correct_external_view_nonreentrant() -> uint256:
    return 42

@external
@payable
@nonreentrant
def correct_external_payable_nonreentrant():
    pass

# Incorrect ordering examples

@view
@external
def incorrect_view_external() -> uint256:
    return 42

@pure
@internal
def incorrect_pure_internal() -> uint256:
    return 123

@nonreentrant
@external
def incorrect_nonreentrant_external():
    pass

@nonreentrant
@view
@external
def incorrect_nonreentrant_view_external() -> uint256:
    return 42

@payable
@nonreentrant
@external
def incorrect_payable_nonreentrant_external():
    pass

# Edge cases

@deploy
def __init__():
    pass

@external
def no_other_modifiers():
    pass

@internal
def internal_only():
    pass

# Functions without explicit visibility (defaults to internal)

@pure
def implicit_internal_pure() -> uint256:
    return 42

@view
def implicit_internal_view() -> uint256:
    return 42

@nonreentrant
def implicit_internal_nonreentrant():
    pass

# Incorrect ordering with implicit internal

@nonreentrant
@view
def incorrect_implicit_internal_nonreentrant_view() -> uint256:
    return 42

# Mixed correct and incorrect orderings
@view
def implicit_internal_view_correct() -> uint256:
    return 42

@nonpayable
def implicit_internal_nonpayable_correct():
    pass
