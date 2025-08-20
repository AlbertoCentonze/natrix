interface ITest:
    def some_interface_pure_function() -> uint256: pure
    def some_interface_other_pure_function() -> uint256: pure
    def some_interface_view_function() -> uint256: view


# This calls a pure function and should raise
@external
def get_value_pure(_token: address) -> uint256:
    return staticcall ITest(_token).some_interface_pure_function()

# This calls multiple pure function and should raise
@external
def get_values_pure(_token: address) -> uint256:
    a: uint256 = staticcall ITest(_token).some_interface_pure_function()
    b: uint256 = staticcall ITest(_token).some_interface_other_pure_function()
    return a + b

# This calls a view function and should not raise
@external
@view
def get_value_view(_token: address) -> uint256:
    return staticcall ITest(_token).some_interface_view_function()


# This calls a mix of pure and view function and should not raise
@external
@view
def get_value_view_and_pure(_token: address) -> uint256:
    a: uint256 = staticcall ITest(_token).some_interface_view_function()
    b: uint256 = staticcall ITest(_token).some_interface_pure_function()
    return a + b
